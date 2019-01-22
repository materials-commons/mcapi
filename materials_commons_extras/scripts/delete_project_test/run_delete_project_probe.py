#!/usr/bin/env python

import rethinkdb as r
from os import environ
from os import path as os_path
from random import randint
from optparse import OptionParser
from time import sleep

import materials_commons_extras.demo_project.demo_project as demo

# noinspection SpellCheckingInspection
TABLES = ['access', 'best_measure_history', 'comments', 'datadir2datafile', 'datadirs',
          'datafiles', 'dataset2datafile', 'dataset2process',
          'dataset2sample', 'datasets', 'deletedprocesses', 'events',
          'experiment2datafile', 'experiment2dataset',
          'experiment2process', 'experiment2sample',
          'experiment_etl_metadata', 'experimentnotes', 'experiments',
          'experimenttasks', 'measurement2datafile',
          'measurements', 'note2item', 'notes', 'process2file', 'process2measurement',
          'process2sample', 'process2setup', 'process2setupfile', 'processes',
          'project2datadir', 'project2datafile', 'project2dataset', 'project2experiment',
          'project2process', 'project2sample', 'projects', 'properties', 'property2measurement',
          'propertyset2property', 'propertysets',
          'sample2datafile', 'sample2propertyset', 'samples',
          'setupproperties', 'setups', 'tag2item', 'tags']
EXCLUDED = ['account_requests', 'background_process', 'file_loads', 'globus_auth_info',
            'globus_uploads', 'templates', 'uploads', 'users']

# NOTE: 'globus_auth_info' does not exist in current test env
# Check: project2dataset
# these tables are not getting reset by project delete:
#             datadirs
#             process2setup
#             properties
#             property2measurement
#             propertyset2property
#             propertysets
#             sample2propertyset
#             setupproperties


class DeleteProjectProbe:
    def __init__(self, db_port, apikey):
        self.conn = r.connect('localhost', db_port, db='materialscommons')
        self.apikey = apikey
        self.pre_condition = {}
        self.post_condition = {}

    def doit(self):
        if not self._env_ok():
            return
        tables = r.table_list().run(self.conn)
        error = False
        for table in tables:
            if (not table in TABLES) and (not table in EXCLUDED):
                print("Warning: table is database but not in code = {}".format(table))
        for table in TABLES:
            if not table in tables:
                print("Warning: table in code but not in database - {}".format(table))
                error = True
        if error:
            print("Found problems - fix and retry")
            return
        tables = TABLES
        for table in tables:
            results = r.table(table).count().run(self.conn)
            self.pre_condition[table] = results
        project = self._build_project()
        print("project id = {}".format(project.id))
        experiments = project.get_all_experiments()
        for exp in experiments:
            print("experiment id = {}".format(exp.id))
        project.delete()
        for table in tables:
            results = r.table(table).count().run(self.conn)
            self.post_condition[table] = results
        for key in tables:
            if not self.pre_condition[key] == self.post_condition[key]:
                print("{} - {} - {}".format(key, self.pre_condition[key], self.post_condition[key]))

    def _build_project(self):
        project_name = self._fake_name("ProjectDeleteTest")
        print("Project name: " + project_name)

        self.test_project_name = project_name

        builder = demo.DemoProject(self._make_test_dir_path(), self.apikey)

        project = builder.build_project()
        project = project.rename(project_name)

        return project

    @staticmethod
    def _env_ok():
        ok = True
        probe = environ['TEST_DATA_DIR'] if 'TEST_DATA_DIR' in environ else None
        if not probe:
            ok = False
            print("Missing env var: TEST_DATA_DIR")
        return ok

    @staticmethod
    def _make_test_dir_path():
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        test_path = os_path.join(test_path, 'demo_project_data')
        return test_path

    @staticmethod
    def _fake_name(prefix):
        number = "%05d" % randint(0, 99999)
        return prefix + number


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-P", "--port", dest="port", type="int", help="rethinkdb port", default=None)
    parser.add_option("-K", "--apikey", dest="apikey", type="string", help="apikey", default=None)

    (options, args) = parser.parse_args()

    env_port = environ['MCDB_PORT'] if 'MCDB_PORT' in environ else None
    port = options.port or env_port or 30815
    print("Using database port = {}".format(port))

    apikey = options.apikey or "totally-bogus"
    print("Using apikey = {}".format(apikey))

    DeleteProjectProbe(port, apikey).doit()
