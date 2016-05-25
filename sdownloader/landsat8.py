import logging
from xml.etree import ElementTree

from usgs import api, USGSError

from .download import S3DownloadMixin, Scenes
from .common import (landsat_scene_interpreter, amazon_s3_url_landsat8, check_create_folder,
                     fetch, google_storage_url_landsat8, remote_file_exists)

from .errors import RemoteFileDoesntExist, USGSInventoryAccessMissing

logger = logging.getLogger('sdownloader')


class Landsat8(S3DownloadMixin):
    """ Landsat8 downloader class """

    def __init__(self, download_dir, usgs_user=None, usgs_pass=None):
        self.download_dir = download_dir
        self.usgs_user = usgs_user
        self.usgs_pass = usgs_pass
        self.scene_interpreter = landsat_scene_interpreter
        self.amazon_s3_url = amazon_s3_url_landsat8

        # Make sure download directory exist
        check_create_folder(self.download_dir)

    def download(self, scenes, bands=None):
        """
        Download scenese from Google Storage or Amazon S3 if bands are provided
        :param scenes:
            A list of scene IDs
        :type scenes:
            List
        :param bands:
            A list of bands. Default value is None.
        :type scenes:
            List
        :returns:
            (List) includes downloaded scenes as key and source as value (aws or google)
        """

        if isinstance(scenes, list):
            scene_objs = Scenes()

            for scene in scenes:

                # for all scenes if bands provided, first check AWS, if the bands exist
                # download them, otherwise use Google and then USGS.
                try:
                    # if bands are not provided, directly go to Goodle and then USGS
                    if not isinstance(bands, list):
                        raise RemoteFileDoesntExist
                    # Always grab MTL.txt and QA band if bands are specified
                    if 'BQA' not in bands:
                        bands.append('QA')

                    if 'MTL' not in bands:
                        bands.append('MTL')

                    scene_objs.merge(self.s3([scene], bands))

                except RemoteFileDoesntExist:
                    try:
                        scene_objs.merge(self.google([scene]))
                    except RemoteFileDoesntExist:
                        scene_objs.merge(self.usgs([scene]))

            return scene_objs

        else:
            raise Exception('Expected sceneIDs list')

    def usgs(self, scenes):
        """ Downloads the image from USGS """

        if not isinstance(scenes, list):
            raise Exception('Expected sceneIDs list')

        scene_objs = Scenes()

        # download from usgs if login information is provided
        if self.usgs_user and self.usgs_pass:
            try:
                api_key = api.login(self.usgs_user, self.usgs_pass)
            except USGSError as e:
                error_tree = ElementTree.fromstring(str(e.message))
                error_text = error_tree.find("SOAP-ENV:Body/SOAP-ENV:Fault/faultstring", api.NAMESPACES).text
                raise USGSInventoryAccessMissing(error_text)

            for scene in scenes:
                download_urls = api.download('LANDSAT_8', 'EE', [scene], api_key=api_key)
                if download_urls:
                    logger.info('Source: USGS EarthExplorer')
                    scene_objs.add_with_files(scene, fetch(download_urls[0], self.download_dir))

                else:
                    raise RemoteFileDoesntExist('{0} not available on AWS S3, Google or USGS Earth Explorer'.format(
                                                ' - '.join(scene)))

            return scene_objs

        raise RemoteFileDoesntExist('{0} not available on AWS S3 or Google Storage'.format(' - '.join(scenes)))

    def google(self, scenes):
        """
        Google Storage Downloader.
        :param scene:
            The scene id
        :type scene:
            List
        :param path:
            The directory path to where the image should be stored
        :type path:
            String
        :returns:
            Boolean
        """

        if not isinstance(scenes, list):
            raise Exception('Expected sceneIDs list')

        scene_objs = Scenes()
        logger.info('Source: Google Storge')

        for scene in scenes:
            sat = landsat_scene_interpreter(scene)
            url = google_storage_url_landsat8(sat)
            remote_file_exists(url)

            scene_objs.add_with_files(scene, fetch(url, self.download_dir))

        return scene_objs
