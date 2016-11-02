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

To Compile
----------

```
  cd to the top level directory of the mcapi repo
  sudo python setup.py install
```

To Test
-------

```
cd to the top level directory of the mcapi repo
pytest -rap --setup-show test
```

And to run test using an individual test class, for example:
```
pytest -rap --setup-show -s test/test_sample_associate.py::TestSampleAssociate  
```