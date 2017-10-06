# build with: python setup.py install --user

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mcapi',
    version='0.8',
    packages=['mcapi', 'mcapi.cli'],
    scripts=['scripts/mc']
)

