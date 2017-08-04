# build with: python setup.py install --user

from distutils.core import setup

setup(
    name='mcapi',
    version='0.8',
    packages=['mcapi', 'mcapi.cli'],
    scripts=['scripts/mc']
)
