import unittest
from random import randint
from mcapi import api
from mcapi import Remote
from mcapi import Config
# from mcapi import list_projects
from mcapi import create_project
from mcapi import create_experiment
from mcapi import create_process_from_template
from mcapi import create_samples

url = 'http://mctest.localhost/api'

def fake_name(prefix):
    number="%05d" % randint(0,99999)
    return prefix+number

class TestWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        config = Config()
        api.set_remote(Remote(config=Config(config={'mcurl': url})))

    def test_is_setup_correctly(self):
        self.assertEqual(api.use_remote().mcurl,url)
        self.assertIsNotNone(api.use_remote().config.params['apikey'])

    def test_workflow(self):
        # # # # DEMO SCRIPT # # # #
        ### login (done externally for now, via apikey)

        # create a project
        project_name = fake_name("Test_Project_")
        project_description = "a test project generated from the api"
        project = create_project(project_name,project_description)
        self.assertIsNotNone(project.id)
        self.assertEqual(project_name,project.name)
        self.assertEqual(project_description,project.description)

        # create an experiment within the project
        experiment_name = "Experiment 1"
        experiment_description = "a test experiment generated from api"
        experiment = create_experiment(project.id,experiment_name,experiment_description)
        self.assertIsNotNone(experiment.id)
        self.assertEqual(experiment_name,experiment.name)
        self.assertEqual(experiment_description,experiment.description)

        ### add files to the project (*) -- not done yet

        # add a sample to the experiment with a create sample process (*)
        template_id = "global_Create Samples"
        create_sample_process = create_process_from_template(project.id,experiment.id,template_id)
        self.assertIsNotNone(create_sample_process)
        self.assertIsNotNone(create_sample_process.id)
        self.assertIsNotNone(create_sample_process.process_type)
        self.assertEqual(create_sample_process.process_type, 'create')
        self.assertTrue(create_sample_process.does_transform)

        sample_names = ['Test Sample 1']
        samples = create_samples(self.base_project_id, self.base_process_id, sample_names)
        self.assertIsNotNone(samples)
        sample = samples[0]
        self.assertIsNotNone(sample)
        self.assertIsNotNone(sample.name)
        self.assertIsNotNone(sample.property_set_id)
        self.assertEqual(sample.name,sample_names[0])

        ### associate previously added file(s) with the create sample process
        ### associate measurements with the sample
        ### fetch previously added file(s) from the experiment/project (*)
        # fetch sample description(s) from the experiment/project
        # fetch measurement(s) from the experiment/project

        # perform a computation on those files, samples, measurements and record that as a computation process (*)

        ### add measures resulting from the computation to the sample/process
        # add the new file from the computation to the project (*)
        # create a Computation process and associate the create-sample version of the sample and some files with that computation
        # add a created/transformed sample as output from the computational process
        ### logout
