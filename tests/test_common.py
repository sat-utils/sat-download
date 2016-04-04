import os
import errno
import shutil
import unittest
from tempfile import mkdtemp

import mock

from sdownloader import common, errors


class Tests(unittest.TestCase):

    def setUp(self):
        self.temp_folder = mkdtemp()
        # self.d = Downloader(download_dir=self.temp_folder)
        self.scene = 'LT81360082013127LGN01'
        self.scene_2 = 'LC82050312014229LGN00'
        self.scene_s3 = 'LC80010092015051LGN00'
        self.scene_s3_2 = 'LC82050312015136LGN00'
        self.scene_size = 59204484

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_folder)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise

    def assertSize(self, url, path):
        remote_size = self.d.get_remote_file_size(url)
        download_size = os.path.getsize(path)

        self.assertEqual(remote_size, download_size)

    @mock.patch('sdownloader.common.download')
    def test_fetch(self, mock_download):
        mock_download.return_value = True

        sat = common.landsat_scene_interpreter(self.scene)
        url = common.google_storage_url_landsat8(sat)

        self.assertTrue(common.fetch(url, self.temp_folder))

    def test_remote_file_size(self):

        url = common.google_storage_url_landsat8(common.landsat_scene_interpreter(self.scene))
        size = common.get_remote_file_size(url)

        self.assertEqual(self.scene_size, size)

    def test_google_storage_url(self):
        sat = common.landsat_scene_interpreter(self.scene)

        string = common.google_storage_url_landsat8(sat)
        expect = 'L8/136/008/LT81360082013127LGN01.tar.bz'
        assert expect in string

    def test_amazon_s3_url(self):
        sat = common.landsat_scene_interpreter(self.scene)
        string = common.amazon_s3_url_landsat8(sat, 11)
        expect = 'L8/136/008/LT81360082013127LGN01/LT81360082013127LGN01_B11.TIF'
        assert expect in string

    def test_remote_file_exist(self):
        # Exists and should return None

        assert common.remote_file_exists(os.path.join(common.S3, 'L8/003/017/LC80030172015001L'
                                                      'GN00/LC80030172015001LGN00_B6.TIF'))

        # Doesn't exist and should raise errror
        with self.assertRaises(errors.RemoteFileDoesntExist):
            common.remote_file_exists(
                os.path.join(
                    common.S3,
                    'L8/003/017/LC80030172015001LGN00/LC80030172015001LGN00_B34.TIF'
                )
            )

        # Doesn't exist and should raise errror
        with self.assertRaises(errors.RemoteFileDoesntExist):
            common.remote_file_exists(
                os.path.join(
                    common.GOOGLE,
                    'L8/003/017/LC80030172015001LGN00/LC80030172015001LGN00_B6.TIF'
                )
            )

        # Exist and shouldn't raise error
        assert common.remote_file_exists(os.path.join(common.GOOGLE, 'L8/003/017/LC80030172015001LGN00.tar.bz'))

    def test_scene_interpreter(self):
        # Test with correct input
        scene = 'LC80030172015001LGN00'
        ouput = common.landsat_scene_interpreter(scene)
        self.assertEqual({'path': '003', 'row': '017', 'sat': 'L8', 'scene': scene}, ouput)

        # Test with incorrect input
        self.assertRaises(Exception, common.landsat_scene_interpreter, 'LC80030172015001LGN')

if __name__ == '__main__':
    unittest.main()