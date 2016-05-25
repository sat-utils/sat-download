import logging

from .download import S3DownloadMixin
from .common import sentinel_scene_interpreter, amazon_s3_url_sentinel2, check_create_folder

logger = logging.getLogger('sdownloader')


class Sentinel2(S3DownloadMixin):
    """ Sentinel2 downloader class """

    def __init__(self, download_dir):
        self.download_dir = download_dir
        self.scene_interpreter = sentinel_scene_interpreter
        self.amazon_s3_url = amazon_s3_url_sentinel2

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
