sat-downloader
++++++++++++++

.. image:: https://travis-ci.org/sat-utils/sat-download.svg?branch=master
    :target: https://travis-ci.org/sat-utils/sat-download

A python library for download Satellite Imagery. Currently support Landsat-8 and Sentinel-2A.


Installation
============

::

    $ python setup.py install

or::

    $ pip install git+git://github.com/sat-utils/sat-download.git@master


Tests
=====

::

    $ python setup.py test


Example
=======

::

  >>> from sdownloader import Landsat8
  >>> from tempfile import mkdtemp
  >>> temp_folder = mkdtemp()
  >>> l = Landsat8(download_dir=temp_folder)
  >>> scenes = l.download(['LC80010092015051LGN00', 'LC82050312015136LGN00'], bands=[4,3,2])
     100%     40.3 MiB       6.2 MiB/s            0:00:00 ETA
     100%     38.1 MiB       6.1 MiB/s            0:00:00 ETA
     100%     38.0 MiB       5.2 MiB/s            0:00:00 ETA
     100%    504.7 KiB     263.1 KiB/s            0:00:00 ETA
     100%      7.4 KiB       7.4 KiB/s            0:00:00 ETA
     100%     60.5 MiB       6.4 MiB/s            0:00:00 ETA
     100%     59.8 MiB       6.9 MiB/s            0:00:00 ETA
     100%     59.2 MiB       7.0 MiB/s            0:00:00 ETA
     100%      2.5 MiB     978.2 KiB/s            0:00:00 ETA
     100%      7.7 KiB       7.7 KiB/s            0:00:00 ETA
  >>> print(scenes)
  [Scenes]: Includes 2 scenes
  >>> [s.name for s in scenes]
  ['LC80010092015051LGN00', 'LC82050312015136LGN00']
  >>> {s.name: s.files for s in scenes}
  {'LC82050312015136LGN00': ['./LC82050312015136LGN00/LC82050312015136LGN00_B4.TIF', './LC82050312015136LGN00/LC82050312015136LGN00_B3.TIF', './LC82050312015136LGN00/LC82050312015136LGN00_B2.TIF', './LC82050312015136LGN00/LC82050312015136LGN00_BQA.TIF', './LC82050312015136LGN00/LC82050312015136LGN00_MTL.txt', './LC82050312015136LGN00/LC82050312015136LGN00_BQA.TIF'], 'LC80010092015051LGN00': ['./LC80010092015051LGN00/LC80010092015051LGN00_B4.TIF', './LC80010092015051LGN00/LC80010092015051LGN00_B3.TIF', './LC80010092015051LGN00/LC80010092015051LGN00_B2.TIF', './LC80010092015051LGN00/LC80010092015051LGN00_BQA.TIF', './LC80010092015051LGN00/LC80010092015051LGN00_MTL.txt']}

