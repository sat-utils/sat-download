import os
import errno
import shutil
import unittest
from tempfile import mkdtemp

import mock

from sdownloader.sentinel2 import Sentinel2


class Tests(unittest.TestCase):

    def setUp(self):
        self.temp_folder = mkdtemp()
        self.scenes = ['S2A_OPER_MSI_L1C_TL_SGS__20160325T150955_A003951_T34RCS_N02.01',
                       'S2A_OPER_MSI_L1C_TL_SGS__20160320T140936_A003879_T37TBG_N02.01']
        self.paths = ['tiles/34/R/CS/2016/3/25/0', 'tiles/37/T/BG/2016/3/20/0']

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_folder)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise

    @mock.patch('sdownloader.sentinel2.fetch')
    def test_download_scene_name(self, fake_fetch):
        """ Test downloading from S3 for a given sceneID """

        fake_fetch.return_value = True

        l = Sentinel2(download_dir=self.temp_folder)
        results = l.s3(self.scenes, [4, 3, 2])

        assert isinstance(results, list)
        assert len(results) == len(self.scenes)
        for i, scene in enumerate(self.scenes):
            self.assertEqual(results[i], os.path.join(self.temp_folder, scene))

    @mock.patch('sdownloader.sentinel2.fetch')
    def test_download_path(self, fake_fetch):
        """ Test downloading from S3 for a given sceneID """

        fake_fetch.return_value = True

        l = Sentinel2(download_dir=self.temp_folder)
        results = l.s3(self.paths, [4, 3, 2])

        assert isinstance(results, list)
        assert len(results) == len(self.paths)
        for i, scene in enumerate(self.paths):
            self.assertEqual(results[i], os.path.join(self.temp_folder, scene.replace('/', '_')))
