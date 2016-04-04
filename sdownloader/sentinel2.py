import logging
from os.path import join

from .common import (sentinel_scene_interpreter, amazon_s3_url_sentinel2, remote_file_exists,
                     check_create_folder, fetch)

logger = logging.getLogger('sdownloader')


class Sentinel2(object):
    """ Sentinel2 downloader class """

    def __init__(self, download_dir):
        self.download_dir = download_dir

        # Make sure download directory exist
        check_create_folder(self.download_dir)

    def download(self, scenes, bands):
        """
        Download scenese Amazon S3. Bands must be provided

        The scenes could either be a scene_id used by sentinel-api or a s3 path (e.g. tiles/34/R/CS/2016/3/25/0)

        :param scenes:
            A list of scenes
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
            return self.s3(scenes, bands)
        else:
            raise Exception('Expected scene list')

    def s3(self, scenes, bands):
        """
        Amazon S3 downloader
        """
        if not isinstance(scenes, list):
            raise Exception('Expected scene list')

        folders = []

        logger.info('Source: AWS S3')
        for scene in scenes:
            path = sentinel_scene_interpreter(scene)

            urls = []

            for band in bands:
                # get url for the band
                url = amazon_s3_url_sentinel2(path, band)

                # make sure it exist
                remote_file_exists(url)
                urls.append(url)

            if '/' in scene:
                scene = scene.replace('/', '_')

            # create folder
            folders.append(check_create_folder(join(self.download_dir, scene)))

            for url in urls:
                fetch(url, self.download_dir)

        return folders
