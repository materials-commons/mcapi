Compiling and Running Tests
===========================

Preconditions
-------------

You must have set up the connection configuration, in a file **config.json**
in a directory **~/.materialscommons**, with the content:
```bash
{
    "apikey": "a1234567890c1234567890c123456789",
    "mcurl": "http://mctest.localhost/api"
}
```

There is a special case for the content of **config.json**; the complete
set of tests requires to predefined users in a special database.
See the next section for details.

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

Dependencies on materialcommons.org and specific database
---------------------------------------------------------

Right the complete set of these tests will only run if you have set 
a "matching version" of materialscommons.org
and have installed a test database that has two users: **another@test.mc** and **test@test.mc**.

Most of the time the matching version of materialscommons.org is the one having the same
branch name: **master** for master and **sprint** for sprint. However, if there is any doubt,
check the **travis.yml** file for the branch you are working in, and look for the git clone
statement that clones materialscommons.org, the 'correct' branch will be indicated there.

To set up the test database, you need to understand how materialscommons.org is determining
its database. In general, the default database is the one that is used for testing.
Specificially, the environment variable **MCDB_FILE** needs either to be cleared (which
will indicate to materialscommons.org to use the default database) or set to the path of
the zip file for that defaults: **materialscommons.org/backend/test_data/test_rethinkdb_dump.tar.gz**.
where **materialscommons.org** is the path to the location of that cloned github repository.
 
In addition, the api key for that test user in that database must be in the configuration file
located at **~/.materialscommons/config.json**; that api key is **totally-bogus**. Thus the
content of the configuration file will have to be:
```bash
{
    "apikey": "totally-bogus",
    "mcurl": "http://mctest.localhost/api"
}
```

You can verify that the dataset is set up correctly and the servers is running correctly by
entering the following url into your browser:
```html
https://mctest.localhost/api/v2/templates?apikey=totally-bogus
```
The returned "value" should be a lot of json. It's actuall the list of all the templates in
Materials Commons.

Libraries
---------
```bash
  pip install --user python-magic
  pip install --user pathlib
```

If you plan to use the casm_mcapi module, you may need to install numpy to support
the matrix representation used by _add_numpy_matrix_measurement
```bash
  pip install --user numpy
```

The full set of libraries used in the project and test can also be
installed using the **requirements.txt** file:
```bash
  pip install -r requirements.txt
```

To Compile
----------

```bash
  cd to the python top level directory of the mcapi repo
  python setup.py install --user
```

To Test
-------

Prior to running the test you will need to set an environment varialbe TEST_DATA_DIR
to point to the directory python/test/test_data. That is:
```bash
  cd to the python top level directory of the python section of the mcapi repo
  source set_test_dir.sh
```

```bash
  cd to the python top level directory of the python section of the mcapi repo
  pytest -rap --setup-show -s test
```

And to run test using an individual test class, for example:
```bash
  pytest -rap --setup-show -s test/mcapi_tests/test_sample_associate.py::TestSampleAssociate  
```

To Generate Coveratge
---------------------

If you wish to generate coverage information, set up as in "To Test" above and them run:
```bash
  cd to the python top level directory of the python section of the mcapi repo
  coverage run -m py.test test
  coverage html --include="*mcapi*" --omit="*test*"
```
The resulting coverage information is in the directory **htmlcov**

To Generate API docs
---------------------

You will have to figure this out from example; see the script **scripts/build-python-api.sh** 
in the project **https://github.com/materials-commons/materials-commons.github.io.git** for an
example of building the API docs using Sphynx.