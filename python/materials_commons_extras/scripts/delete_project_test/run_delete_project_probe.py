#!/usr/bin/env python

import rethinkdb as r
from os import environ
from os import path as os_path
from random import randint
from optparse import OptionParser

import materials_commons_extras.demo_project.demo_project as demo

# noinspection SpellCheckingInspection
TABLES = ['access', 'best_measure_history', 'comments', 'datadir2datafile', 'datadirs',
          'datafiles', 'dataset2datafile', 'dataset2experimentnote', 'dataset2process',
          'dataset2sample', 'datasets', 'deletedprocesses', 'elements', 'events',
          'experiment2datafile', 'experiment2dataset', 'experiment2experimentnote',
          'experiment2experimenttask', 'experiment2process', 'experiment2sample',
          'experiment_etl_metadata', 'experimentnotes', 'experiments', 'experimenttask2process',
          'experimenttasks', 'globus_auth_info', 'machines', 'measurement2datafile',
          'measurements', 'note2item', 'notes', 'process2file', 'process2measurement',
          'process2sample', 'process2setup', 'process2setupfile', 'processes',
          'project2datadir', 'project2datafile', 'project2dataset', 'project2experiment',
          'project2process', 'project2sample', 'projects', 'properties', 'property2measurement',
          'propertyset2property', 'propertysets', 'review2item', 'reviews', 'runs',
          'sample2datafile', 'sample2propertyset', 'sample2sample', 'samples',
          'setupproperties', 'setups', 'shares', 'tag2item', 'tags',
          'ui', 'uploads']


class DeleteProjectProbe:
    def __init__(self, db_port):
        self.conn = r.connect('localhost', db_port, db='materialscommons')
        self.precondition = {}
        self.postcondition = {}

    def doit(self):
        # tables = r.table_list().run(self.conn)
        # print(tables)
        tables = TABLES
        for table in tables:
            results = r.table(table).pluck('owner').run(self.conn)
            if results:
                results = list(results)
                if len(results) > 0 and results[0]:
                    results = results[0]
            print("{} --> {}".format(table, results))
        # for table in tables:
        #     results = r.table(table).count().run(self.conn)
        #     self.precondition[table] = results
        # project = self._build_project()
        # project.delete()
        # for table in tables:
        #     results = r.table(table).count().run(self.conn)
        #     self.postcondition[table] = results
        # for key in tables:
        #     mark = "<--" if not self.precondition[key] == self.postcondition[key] else ""
        #     print("{} - {} - {}  {}".format(key, self.precondition[key], self.postcondition[key], mark))
        #     # print("{} -- {}".format(key, self.postcondition[key]))

    def _build_project(self):
        project_name = self._fake_name("ProjectDeleteTest")
        # print("")
        # print("Project name: " + project_name)

        self.test_project_name = project_name

        builder = demo.DemoProject(self._make_test_dir_path())

        project = builder.build_project()
        project = project.rename(project_name)

        return project

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
    parser.add_option("-P", "--port", dest="port", type="int", help="rethinkdb port", default=30815)

    (options, args) = parser.parse_args()

    port = options.port
    print("Using database port = {}".format(port))

    DeleteProjectProbe(port).doit()
