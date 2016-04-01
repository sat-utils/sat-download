import logging
from os.path import join
from xml.etree import ElementTree

from usgs import api, USGSError

from .common import (check_create_folder, fetch, landsat_scene_interpreter, google_storage_url_landsat8,
                     remote_file_exists, amazon_s3_url_landsat8)
from .errors import RemoteFileDoesntExist, USGSInventoryAccessMissing

logger = logging.getLogger('sdownloader')


class Landsat8(object):
    """ Landsat8 downloader class """

    def __init__(self, download_dir=None, usgs_user=None, usgs_pass=None):
        self.download_dir = download_dir
        self.usgs_user = usgs_user
        self.usgs_pass = usgs_pass

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
            files = []

            for scene in scenes:

                # for all scenes if bands provided, first check AWS, if the bands exist
                # download them, otherwise use Google and then USGS.
                try:
                    # if bands are not provided, directly go to Goodle and then USGS
                    if not isinstance(bands, list):
                        raise RemoteFileDoesntExist
                    files.append(self.s3([scene], bands))

                except RemoteFileDoesntExist:
                    try:
                        files.append(self.google([scene], self.download_dir))
                    except RemoteFileDoesntExist:
                        files.append(self.usgs([scene], self.download_dir))

            return files

        else:
            raise Exception('Expected sceneIDs list')

    def usgs(self, scenes):
        """ Downloads the image from USGS """

        if not isinstance(scenes, list):
            raise Exception('Expected sceneIDs list')

        files = []

        # download from usgs if login information is provided
        if self.usgs_user and self.usgs_pass:
            try:
                api_key = api.login(self.usgs_user, self.usgs_pass)
            except USGSError as e:
                error_tree = ElementTree.fromstring(str(e.message))
                error_text = error_tree.find("SOAP-ENV:Body/SOAP-ENV:Fault/faultstring", api.NAMESPACES).text
                raise USGSInventoryAccessMissing(error_text)

            download_urls = api.download('LANDSAT_8', 'EE', scenes, api_key=api_key)
            if download_urls:
                logger.info('Source: USGS EarthExplorer')
                for url in download_urls:
                    files.append(fetch(url, self.download_dir))

                return files
            else:
                raise RemoteFileDoesntExist('{0} not available on AWS S3, Google or USGS Earth Explorer'.format(
                                            ' - '.join(scenes)))
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

        files = []
        logger.info('Source: Google Storge')

        for scene in scenes:

            sat = landsat_scene_interpreter(scene)
            url = google_storage_url_landsat8(sat)
            remote_file_exists(url)

            files.append(fetch(url, self.download_dir))

        return files

    def s3(self, scenes, bands):
        """
        Amazon S3 downloader
        """
        if not isinstance(scenes, list):
            raise Exception('Expected sceneIDs list')

        folders = []

        logger.info('Source: AWS S3')
        for scene in scenes:
            sat = landsat_scene_interpreter(scene)

            # Always grab MTL.txt and QA band if bands are specified
            if 'BQA' not in bands:
                bands.append('QA')

            if 'MTL' not in bands:
                bands.append('MTL')

            urls = []

            for band in bands:
                # get url for the band
                url = amazon_s3_url_landsat8(sat, band)

                # make sure it exist
                remote_file_exists(url)
                urls.append(url)

            # create folder
            folders.append(check_create_folder(join(self.download_dir, scene)))

            for url in urls:
                fetch(url, self.download_dir)

        return folders
