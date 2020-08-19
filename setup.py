# build with: python setup.py install --user

from setuptools import setup, find_namespace_packages


try:
    with open('materials_commons/api/VERSION.txt') as f:
        version = f.read().strip()
except IOError:
    version = '2.0b0'


setup(
    name='materials_commons-api',
    version=version,
    description='API interface to Materials Commons',
    long_description="""This package contains the materials_commons.api module. This module is an interface
    to the Materials Commons project. We assume you have used (or are otherwise familiar with) the Materials
    Commons web site, https://materialscommons.org/, or a similar site based on the
    Materials Commons code (https://github.com/materials-commons/materialscommons), and intend to use these 
    tools in that context.""",
    url='https://materials-commons.github.io/python-api/',
    author='Materials Commons development team',
    author_email='materials-commons-authors@umich.edu',
    license='MIT',
    package_data={'api': ['VERSION.txt']},
    include_package_data=True,
    packages=['materials_commons.api'],
    zip_safe=False,
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8'
    ],
    keywords='materials science mc materials-commons prisms',
    install_requires=[
        "requests",
        "urllib3",
    ]
)
