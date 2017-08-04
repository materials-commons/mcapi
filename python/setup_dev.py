# build with: python setup_dev.py install --user

from distutils.core import setup

setup(
    name='mcapi',
    version='0.8',
    packages=['mcapi', 'mcapi.cli'],
    scripts=['scripts/mc']
)

setup(
    name='demo_project',
    version='0.9',
    packages=['demo_project']
)
