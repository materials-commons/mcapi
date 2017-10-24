# build with: python setup.py install --user

from setuptools import setup, find_packages

setup(
    name='materials-commons',
    version='0.5.5',
    description='The Materials Commons tool set',
    long_description="""This package contains three modules:
    (1) materials-commons.mcapi, the Materials Commons Python API, an interface 
    to the Materials Commons servers; (2) materials-commons.cli, the 
    Material Commons command line interface which is built on the API and provides
    command line access to the Materials Commons servers; and (3) materials-commons.demo-project
    which provides a tool for building a demo project in your account on a Materials Commons
    servers. We assume you have used (or are otherwise familiar with) the Materials 
    Commons web site, https://materialscommons.org/, or a similar site based on the
    materials commons code (https://github.com/materials-commons/materialscommons.org),
    and intend to use these tools in that context""",
    url='https://materials-commons.github.io/python-api/',
    author='Materials Commons development team',
    author_email='materials-commons-authors@umich.edu',
    license='MIT',
    packages = ['materials-commons', 'materials-commons.api',
              'materials-commons.cli', 'materials-commons.demo-project'],
    scripts=['scripts/mc'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='materials science mc lift prisms',
    install_requires=["requests", "rethinkdb","pathlib", "numpy", "pandas",
                      "tabulate", "sortedcontainers"
                      ]
)
