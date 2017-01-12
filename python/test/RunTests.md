Compiling and Running Tests
===========================

Preconditions
-------------

You must have set up the connection configuration, in a file **config.jason**
in a directory **~/.materialscommons**, with the content:
```
{
    "apikey": "a1234567890c1234567890c123456789",
    "mcurl": "http://mctest.localhost/api"
}
```
Where 'apikey' is your **apikey** and 'mcurl' is the base url of the
api connection on the host being tested (usually your localhost version
of Materials Commons).

To obtain your API key, log into the site that you are running the tests on
(e.g. 'mcurl', above) and under the user-name pull down (upper right corner
of the header bar of main pages) locate the 'API Key' option. This will display a page
with a link to click ('Show API Key') which will show that value of your API key.

Treat you API key as a username/password, because it gives the holder of the key
access to all the data that you have access to. If you wish to reset your key,
there is an option to do so on this same page. When you reset you key, remember to
also update it in the .materialscommons/config.jason file.

Libraries
---------
```
  pip install --user python-magic
  pip install --user pathlib
```

To Compile
----------

```
  cd to the python top level directory of the mcapi repo
  python setup.py install --user
```

To Test
-------

Prior to running the test you will need to set an environment varialbe TEST_DATA_DIR
to point to the directory python/test/test_data. That is:
```
  cd to the python top level directory of the mcapi repo
  pushd test/test_data
  export TEST_DATA_DIR=`pwd`
  popd
```

```
  cd to the python top level directory of the mcapi repo
  pytest -rap --setup-show test
```

And to run test using an individual test class, for example:
```
  pytest -rap --setup-show -s test/test_sample_associate.py::TestSampleAssociate  
```