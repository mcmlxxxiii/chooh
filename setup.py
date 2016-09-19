# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='chooh',
      version='0.1',
      description='Utility for working with CouchDB design document applications (couchapps).',
      url='http://github.com/mcmlxxxiii/chooh',
      author='Mykhaylo Gavrylyuk',
      author_email='gavrylyuk@gmail.com',
      license='MIT',
      packages=[
          'chooh',
          'chooh.core',
          'chooh.contrib',
          'chooh.contrib.bundling',
          'chooh.contrib.bundling.bundlers',
          'chooh.contrib.bundling.processors',
          'chooh.util'
      ],
      scripts=['bin/chooh'],
      install_requires=[
          'docopt==0.6.2',
          'couchdbkit==0.6.5',
          'pyyaml==3.12',
          'watchdog==0.8.3'
      ],
      zip_safe=False)
