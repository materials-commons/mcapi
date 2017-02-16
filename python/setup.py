# build with: python setup.py install --user

from distutils.core import setup

setup(
    name='mcapi',
    version='0.5',
    packages=['mcapi']
)

setup(
    name='casm_mcapi',
    version='0.2',
    packages=['casm_mcapi']
)

setup(
    name='demo_project',
    version='0.2',
    packages=['demo_project']
)

setup(
    name='mcapi_dist',
    version='0.1',
    packages=['demo_project','mcapi']
)