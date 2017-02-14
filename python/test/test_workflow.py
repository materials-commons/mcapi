import unittest
from random import randint
from os import environ
from os import path as os_path
from mcapi import create_project, Template
from mcapi import set_remote_config_url, get_remote_config_url
from mcapi import get_process_from_id
from mcapi import Sample

url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)

    def test_is_setup_correctly(self):
        self.assertEqual(get_remote_config_url(), url)

    def test_workflow(self):

        # #-# the workflow #-#
        project_name = "Workflow Project - test001"
        project_description = "a test project generated from api"
        project = create_project(
            name=project_name,
            description=project_description)

        experiment_name = fake_name("Experiment-")
        experiment_description = "a test experiment generated from api"
        experiment = project.create_experiment(
            name=experiment_name,
            description=experiment_description)

        create_sample_process = experiment.create_process_from_template(Template.create)
        create_sample_process.add_name("Create Simulation Sample")

        sample_name = 'Test Sample 1'
        samples = create_sample_process.create_samples(
            sample_names=[sample_name]
        )
        print "----"
        print samples
        print Sample(data=samples[0].input_data).processes
        print "----"

        sample = samples [0]
        print "----"
        print sample.processes
        print "----"

        experiment.fetch_and_add_samples()
        samples_from_experiment = experiment.samples
        sample_from_experiment = samples_from_experiment[0]

        print "----"
        print sample_from_experiment.processes
        print "----"

        filepath_for_sample = self.make_test_dir_path('sem.tif')
        filename_for_sample = "SampleFile.tif"
        sample_file = project.add_file_using_directory(
            project.add_directory("/FilesForSample"),
            filename_for_sample,
            filepath_for_sample
        )
        create_sample_process.add_files([sample_file])
        create_sample_process = get_process_from_id(project,experiment,create_sample_process.id)

        compute_process = experiment. \
            create_process_from_template(Template.compute). \
            add_samples_to_process([sample])

        compute_process.add_name("Monte Carlo Simulation")

        compute_process.set_value_of_setup_property('number_of_processors',5)
        compute_process.set_value_of_setup_property('memory_per_processor',16)
        compute_process.set_unit_of_setup_property('memory_per_processor','gb')
        compute_process.set_value_of_setup_property('walltime',12)
        compute_process.set_unit_of_setup_property('walltime','h')
        compute_process.set_value_of_setup_property('submit_script',"exec.sh")
        compute_process = compute_process.update_setup_properties([
                'number_of_processors','memory_per_processor','walltime','submit_script'
        ])

        filepath_for_compute = self.make_test_dir_path('fractal.jpg')
        filename_for_compute = "ResultsFile.jpg"
        compute_file = project.add_file_using_directory(
            project.add_directory("/FilesForCompute"),
            filename_for_compute,
            filepath_for_compute
        )
        compute_process.add_files([compute_file])
        compute_process = get_process_from_id(project,experiment,compute_process.id)

        measurement_data = {
            "name":"Composition",
            "attribute":"composition",
            "otype":"composition",
            "unit":"at%",
            "value":[
                {"element":"Al","value":94},
                {"element":"Ca","value":1},
                {"element":"Zr","value":5}],
            "is_best_measure":True
        }
        measurement = create_sample_process.create_measurement(data=measurement_data)

        measurement_property = {
                    "name":"Composition",
                    "attribute":"composition"
                }
        create_sample_process_updated = \
            create_sample_process.\
            set_measurements_for_process_samples(\
                measurement_property, [measurement])

        # #-# tests #-# #
        self.assertIsNotNone(project.id)
        self.assertEqual(project_name, project.name)
        self.assertTrue(project_description in project.description)

        self.assertIsNotNone(experiment.id)
        self.assertEqual(experiment_name, experiment.name)
        self.assertEqual(experiment_description, experiment.description)

        self.assertIsNotNone(create_sample_process)
        self.assertIsNotNone(create_sample_process.id)
        self.assertIsNotNone(create_sample_process.process_type)
        self.assertEqual(create_sample_process.process_type, 'create')
        self.assertTrue(create_sample_process.does_transform)

        self.assertIsNotNone(sample)
        self.assertIsNotNone(sample.name)
        self.assertIsNotNone(sample.property_set_id)
        self.assertEqual(sample.name, sample_name)

        self.assertEqual(sample.id,sample_from_experiment.id)
        self.assertEqual(sample.project.id,sample_from_experiment.project.id)
        self.assertEqual(sample_from_experiment.experiment.id,experiment.id)

        self.assertIsNotNone(sample_file)
        self.assertIsNotNone(sample_file.name)
        self.assertEqual(sample_file.name, filename_for_sample)

        self.assertIsNotNone(create_sample_process.files)
        self.assertEqual(len(create_sample_process.files), 1)
        file1 = create_sample_process.files[0]
        self.assertIsNotNone(file1)
        self.assertIsNotNone(file1.id)
        self.assertEqual(file1.id,sample_file.id)


        self.assertIsNotNone(compute_process)
        self.assertIsNotNone(compute_process.id)
        self.assertIsNotNone(compute_process.process_type)
        self.assertEqual(compute_process.process_type, 'analysis')
        self.assertFalse(compute_process.does_transform)

        prop = compute_process.get_setup_properties_as_dictionary()['walltime']
        self.assertEqual(prop.value,12)
        self.assertEqual(prop.unit,'h')
        prop = compute_process.get_setup_properties_as_dictionary()['memory_per_processor']
        self.assertEqual(prop.value,16)
        self.assertEqual(prop.unit,'gb')
        prop = compute_process.get_setup_properties_as_dictionary()['number_of_processors']
        self.assertEqual(prop.value,5)
        prop = compute_process.get_setup_properties_as_dictionary()['submit_script']
        self.assertEqual(prop.value,"exec.sh")

        self.assertIsNotNone(compute_file)
        self.assertIsNotNone(compute_file.name)
        self.assertEqual(compute_file.name, filename_for_compute)

        self.assertIsNotNone(compute_process.files)
        self.assertEqual(len(compute_process.files), 1)
        file2 = compute_process.files[0]
        self.assertIsNotNone(file2)
        self.assertIsNotNone(file2.id)
        self.assertEqual(file2.id, compute_file.id)

        measurement_out = create_sample_process_updated.measurements[0]
        self.assertEqual(measurement_out.name,measurement.name)
        composition = measurement_out
        self.assertEqual(composition.name,"Composition")
        self.assertEqual(composition.attribute,"composition")
        self.assertEqual(composition.otype,"composition")
        self.assertEqual(composition.unit,"at%")
        value_list = composition.value
        self.assertEqual(value_list[0]['element'],"Al")
        self.assertEqual(value_list[0]['value'],94)
        self.assertEqual(value_list[1]['element'],"Ca")
        self.assertEqual(value_list[1]['value'],1)
        self.assertEqual(value_list[2]['element'],"Zr")
        self.assertEqual(value_list[2]['value'],5)


    def make_test_dir_path(self, file_name):
        self.assertTrue('TEST_DATA_DIR' in environ)
        test_path = os_path.abspath(environ['TEST_DATA_DIR'])
        self.assertIsNotNone(test_path)
        self.assertTrue(os_path.isdir(test_path))
        test_file = os_path.join(test_path, 'test_upload_data', file_name)
        self.assertTrue(os_path.isfile(test_file))
        return test_file
