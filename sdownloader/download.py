import os
import glob
import logging
import tarfile
import subprocess

from .common import remote_file_exists, check_create_folder, fetch

logger = logging.getLogger('sdownloader')


class Scene(object):

    def __init__(self, name, files=None):
        self.name = name
        self.zipped = False
        self.files = []
        self.zip_file = None
        self.band_files = []

        if isinstance(files, str):
            self.add(files)
        elif isinstance(files, list):
            for f in files:
                self.add(f)

    def add(self, f):
        zip_formats = ['.gz', '.bz', '.bz2']
        if os.path.splitext(os.path.basename(f))[-1] in zip_formats:
            self.zipped = True
            self.zip_file = f
        else:
            self.band_files.append(f)
        self.files.append(f)

    def unzip(self, path=None):

        if not path:
            path = os.path.join(os.path.split(self.zip_file)[0], self.name)

        if not self.zipped:
            raise Exception('Scene does not have a zip file associated with it')
        else:
            try:
                tar = tarfile.open(self.zip_file, 'r')
                tar.extractall(path=path)
                tar.close()
            except tarfile.ReadError:
                subprocess.check_call(['tar', '-xf', self.zip_file, '-C', path])

            formats = ['*.tif', '*.TIF', '*.jp2']

            for f in formats:
                for image in glob.glob(os.path.join(path, f)):
                    self.add(image)

            self.zipped = False

    def __str__(self):
        return self.name


class Scenes(object):

    def __init__(self, scenes=[]):
        self.scenes_dict = {}
        self.scenes_list = []
        for scene in scenes:
            self.add(self.validate(scene))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.scenes_list[key]
        elif isinstance(key, str):
            return self.scenes_dict[key]
        else:
            raise Exception('Key is not supported.')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.scenes_list[key] = self.validate(value)
        elif isinstance(key, str):
            self.scenes_dict[key] = self.validate(value)
        else:
            raise Exception('Key is not supported.')

    def __len__(self):
        return len(self.scenes_dict.keys())

    def __str__(self):
        return '[Scenes]: Includes %s scenes' % len(self)

    def add(self, scene):
        self.scenes_list.append(self.validate(scene))
        self.scenes_dict[scene.name] = scene

    def add_with_files(self, name, files):
        self.add(Scene(name, files))

    def validate(self, scene):
        if not isinstance(scene, Scene):
            raise Exception('scene must be an instance of Scene')

        return scene

    def merge(self, scenes):
        if not isinstance(scenes, Scenes):
            raise Exception('scenes must be an instance of Scenes')

        for s in scenes:
            self.add(s)

    @property
    def scenes(self):
        return [s.name for s in self]

    def unzip(self):
        for i, scene in enumerate(self):
            scene.unzip()


class S3DownloadMixin(object):

    def s3(self, scenes, bands):
        """
        Amazon S3 downloader
        """
        if not isinstance(scenes, list):
            raise Exception('Expected scene list')

        scene_objs = Scenes()

        logger.info('Source: AWS S3')
        for scene in scenes:
            files = []

            path = self.scene_interpreter(scene)

            urls = []

            for band in bands:
                # get url for the band
                url = self.amazon_s3_url(path, band)

                # make sure it exist
                remote_file_exists(url)
                urls.append(url)

            if '/' in scene:
                scene_file = scene.replace('/', '_')
            else:
                scene_file = scene

            folder = os.path.join(self.download_dir, scene_file)
            # create folder
            check_create_folder(folder)

            for url in urls:
                files.append(fetch(url, folder))

            scene_objs.add_with_files(scene, files)

        return scene_objs
