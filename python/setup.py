# build with: python setup.py install --user

from setuptools import setup

setup(
    name='mcapi',
    version='0.8',
    description='The Materials Commons Python API',
    long_description="""This is an implementation of the Python API, an interface to
    the Materials Commons server. We assume that the reader has used (or is otherwise
    familiar with) the Materials Commons web site, https://materialscommons.org/ or a
    similar site based on the materials commons rest-interface server, and intends
    to use this API in that context""",
    url='https://materials-commons.github.io/python-api/',
    author='Materials Commons development team',
    author_email='help@materialscommons.org',
    liscense='MIT',
    packages=['mcapi', 'mcapi.cli'],
    scripts=['scripts/mc'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Laboratory Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='materials science mc lift prisims',
    install_requires=["requests", "rethinkdb","pathlib", "numpy", "pandas",
                      "tabulate", "sortedcontainers"
                      ]
)

setup(
    name="mc_demo_project",
    version='0.1',
    packages=['demo_project'],
    description='Demo project builder for the Materials Commons Python API',
    long_description="""This is a companion package to the Materials Commons Python API""",
    url='https://materials-commons.github.io/python-api/',
    author='Materials Commons development team',
    author_email='help@materialscommons.org',
    liscense='MIT',
    classifiers = [
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Laboratory Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords = 'materials science mc lift prisims',
    install_requires=['mcapi'],
    data_files = [
        ("demo_data_files", ['demo_project/demo_project_data'])
    ]
)
