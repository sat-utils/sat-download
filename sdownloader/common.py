import re
import logging
from os import makedirs
from os.path import join, exists, getsize

import requests
from homura import download

from .errors import IncorrectLandsat8SceneId, RemoteFileDoesntExist

logger = logging.getLogger('sdownloader')


def landsat_scene_interpreter(scene_name):
    """ Retrieve row, path and date from Landsat-8 sceneID.
    :param scene_name:
        The scene ID.
    :type scene:
        String
    :returns:
        dict
    :Example output:
    >>> anatomy = {
            'path': None,
            'row': None,
            'sat': None,
            'scene': scene
        }
    """

    anatomy = {
        'path': None,
        'row': None,
        'sat': None,
        'scene': scene_name
    }

    if isinstance(scene_name, str) and len(scene_name) == 21:
        anatomy['path'] = scene_name[3:6]
        anatomy['row'] = scene_name[6:9]
        anatomy['sat'] = 'L' + scene_name[2:3]

        return anatomy
    else:
        raise IncorrectLandsat8SceneId('Received incorrect scene')


def check_create_folder(folder_path):
    """ Check whether a folder exists, if not the folder is created.
    :param folder_path:
        Path to the folder
    :type folder_path:
        String
    :returns:
        (String) the path to the folder
    """
    if not exists(folder_path):
        makedirs(folder_path)

    return folder_path


def get_remote_file_size(url):
    """ Gets the filesize of a remote file.
    :param url:
        The url that has to be checked.
    :type url:
        String
    :returns:
        int
    """
    headers = requests.head(url).headers
    return int(headers['content-length'])


def remote_file_exists(url):
        """ Checks whether the remote file exists.
        :param url:
            The url that has to be checked.
        :type url:
            String
        :returns:
            **True** if remote file exists and **False** if it doesn't exist.
        """
        status = requests.head(url).status_code

        if status == 200:
            return True
        else:
            raise RemoteFileDoesntExist


def remove_slash(value):
    """ Removes slash from beginning and end of a string """
    assert isinstance(value, str)
    return re.sub('(^\/|\/$)', '', value)


def url_builder(segments):
    """ Join segments with '/' slash to create a path/url """
    # Only accept list or tuple
    assert (isinstance(segments, list) or isinstance(segments, tuple))
    return "/".join([remove_slash(s) for s in segments])


def amazon_s3_url_landsat8(sat, band):
        """
        Return an amazon s3 url for a landsat8 scene band
        :param sat:
            Expects an object created by landsat_scene_interpreter function
        :type sat:
            dict
        :param filename:
            The filename that has to be downloaded from Amazon
        :type filename:
            String
        :returns:
            (String) The URL to a S3 file
        """
        s3 = 'http://landsat-pds.s3.amazonaws.com/'

        if band != 'MTL':
            filename = '%s_B%s.TIF' % (sat['scene'], band)
        elif band == 'MTL':
            filename = '%s_%s.txt' % (sat['scene'], band)
        else:
            raise IncorrectLandsat8SceneId('Band number provided is not correct!')

        return url_builder([s3, sat['sat'], sat['path'], sat['row'], sat['scene'], filename])


def google_storage_url_landsat8(sat):
    """
    Returns a google storage url for a landsat8 scene.
    :param sat:
        Expects an object created by landsat_scene_interpreter function
    :type sat:
        dict
    :returns:
        (String) The URL to a google storage file
    """
    print(sat)
    filename = sat['scene'] + '.tar.bz'
    google = 'http://storage.googleapis.com/earthengine-public/landsat/'
    return url_builder([google, sat['sat'], sat['path'], sat['row'], filename])


def fetch(url, path):
    """ Downloads a given url to a give path.
    :param url:
        The url to be downloaded.
    :type url:
        String
    :param path:
        The directory path to where the image should be stored
    :type path:
        String
    :param filename:
        The filename that has to be downloaded
    :type filename:
        String
    :returns:
        Boolean
    """

    segments = url.split('/')
    filename = segments[-1]

    # remove query parameters from the filename
    filename = filename.split('?')[0]

    if exists(join(path, filename)):
        size = getsize(join(path, filename))
        if size == get_remote_file_size(url):
            logger.info('{0} already exists on your system'.format(filename))

    else:
        download(url, path)
    logger.info('stored at {0}'.format(path))

    return join(path, filename)
