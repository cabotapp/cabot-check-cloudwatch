#!/usr/bin/env python

from pip.req import parse_requirements
from setuptools import find_packages, setup

requirements = [str(req.req) for req in parse_requirements('requirements.txt', session=False)]

setup(name='cabot_check_cloudwatch',
      version='0.1.0',
      description='A clouwatch check plugin for Cabot by Arachnys',
      author='Arachnys',
      author_email='techteam@arachnys.com',
      url='http://cabotapp.com',
      install_requires=requirements,
      packages=find_packages(),
    )
