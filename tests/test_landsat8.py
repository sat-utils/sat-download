import os
import errno
import shutil
import unittest
from tempfile import mkdtemp

import mock

from sdownloader.download import Scenes
from sdownloader.landsat8 import Landsat8


class Tests(unittest.TestCase):

    def setUp(self):
        self.temp_folder = mkdtemp()
        self.s3_scenes = ['LC80010092015051LGN00', 'LC82050312015136LGN00']
        self.all_scenes = ['LC80010092015051LGN00', 'LC82050312015136LGN00', 'LT81360082013127LGN01',
                           'LC82050312014229LGN00']
        self.scene_size = 59204484

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_folder)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise

    @mock.patch('sdownloader.download.fetch')
    def test_s3(self, fake_fetch):
        """ Test downloading from S3 for a given sceneID """

        fake_fetch.return_value = 'file.tif'

        l = Landsat8(download_dir=self.temp_folder)
        results = l.s3(self.s3_scenes, [4, 3, 2])

        self.assertTrue(isinstance(results, Scenes))
        self.assertEqual(self.s3_scenes, results.scenes)
        self.assertEqual(len(results[self.s3_scenes[0]].files), 3)

    @mock.patch('sdownloader.common.download')
    def test_google(self, fake_fetch):
        """ Test downloading from google for a given sceneID """

        fake_fetch.return_value = True

        l = Landsat8(download_dir=self.temp_folder)
        results = l.google(self.all_scenes)

        self.assertTrue(isinstance(results, Scenes))
        self.assertEqual(len(results), len(self.all_scenes))
        for i, scene in enumerate(self.all_scenes):
            self.assertEqual(results[scene].zip_file, os.path.join(self.temp_folder, scene + '.tar.bz'))

    @mock.patch('sdownloader.landsat8.api.login')
    @mock.patch('sdownloader.landsat8.api.download')
    @mock.patch('sdownloader.common.download')
    def test_usgs(self, fake_fetch, fake_api, fake_login):
        """ Test downloading from google for a given sceneID """

        fake_login.return_value = True
        fake_fetch.return_value = 'file.tar.bz'
        fake_api.return_value = ['example.com/%s.tar.bz' % scene for scene in self.all_scenes]

        l = Landsat8(download_dir=self.temp_folder, usgs_user='test', usgs_pass='test')
        results = l.usgs(self.all_scenes)

        self.assertTrue(isinstance(results, Scenes))
        self.assertEqual(len(results), len(self.all_scenes))
        self.assertEqual(results[0].zip_file, os.path.join(self.temp_folder, self.all_scenes[0] + '.tar.bz'))

    @mock.patch('sdownloader.landsat8.Landsat8.google')
    def test_download_google_when_amazon_is_unavailable(self, fake_google):
        """ Test whether google or amazon are correctly selected based on input """

        fake_google.return_value = []

        # Test if google is used when an image from 2014 is passed even if bands are provided
        scenes = [self.all_scenes[-1]]
        l = Landsat8(download_dir=self.temp_folder)
        l.download(scenes, bands=[432])
        fake_google.assert_called_with(scenes)
