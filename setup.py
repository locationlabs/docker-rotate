#!/usr/bin/env python

from setuptools import setup, find_packages

__version__ = '3.2'

__build__ = ''

setup(name='dockerrotate',
      version=__version__ + __build__,
      description='Docker image rotation tool',
      author='Location Labs',
      author_email='info@locationlabs.com',
      url='http://locationlabs.com',
      packages=find_packages(exclude=['*.tests']),
      install_requires=[
          'docker-py>=1.6.0',
          'python-dateutil>=2.4.0',
      ],
      entry_points={
          'console_scripts': [
              'docker-rotate = dockerrotate.main:main',
          ]
      },
      )
