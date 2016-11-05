import unittest
from random import randint
from mcapi import api
from mcapi import Remote
from mcapi import Config
from mcapi import Project
from mcapi import list_projects
from mcapi import create_project

url = 'http://mctest.localhost/api'

def fake_name(prefix):
    number="%05d" % randint(0,99999)
    return prefix+number

class TestProject(unittest.TestCase):
    def setup(self):
        config = Config()
        api.set_remote(Remote(config=Config(config={'mcurl': url})))

    def test_is_setup_correctly(self):
        self.assertEqual(api.use_remote().mcurl,url)
        self.assertIsNotNone(api.use_remote().config.params['apikey'])

    def test_list_projects_object(self):
        projects = list_projects()
        one_project = projects[0]
        self.assertIsNotNone(one_project.name)
        self.assertTrue(isinstance(one_project,Project))
        self.verify_project(one_project)

    def test_create_project_api(self):
        name = fake_name("TestProject-")
        print("fake name for API call: ", name)
        description = "Test project generated by automated test"
        ids = api.create_project(name,description)
        self.assertIsNotNone(ids)
        print ids
        self.assertTrue('project_id' in ids.keys())
        self.assertTrue('datadir_id' in ids.keys())

    def test_create_project_object(self):
        name = fake_name("TestProject-")
        description = "Test project generated by automated test"
        project = create_project(name,description)
        print project
        self.verify_project(project)
        self.assertEqual(name,project.name)
        self.assertEqual(description,project.description)

    def verify_project(self,project):
        self.assertIsNotNone(project.name)
        self.assertIsNotNone(project.description)
        self.assertIsNotNone(project.id)
        self.assertNotEqual(project.name,"")
        self.assertEqual(project.status,"active")
        self.assertTrue(isinstance(project.experiments,int))
        self.assertTrue(isinstance(project.files,int))
        self.assertTrue(isinstance(project.processes,int))
