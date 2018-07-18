import unittest
import pytest
from random import randint
from materials_commons.api import api


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix + number


class TestApiMetadataRaw(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "another@test.mc"
        cls.apikey = "another-bogus-account"
        cls.access_user = "test@test.mc"
        project_name = fake_name("TestApikeyProject-")
        description = "Test project generated by automated test"
        raw_data = api.create_project(project_name, description, apikey=cls.apikey)
        cls.project_id = raw_data['id']
        experiment_name = fake_name("TestExperiment-")
        experiment_description = "Test experiment generated by automated test"
        experiment_raw = api.create_experiment(
            cls.project_id, experiment_name, experiment_description, apikey=cls.apikey)
        cls.experiment_id = experiment_raw['id']

    def test_create_metadata_raw(self):
        fake_metadata = _make_reasonable_metadata()
        self.assertIsNotNone(fake_metadata)
        experiment_id = self.experiment_id
        json = fake_metadata
        results = api.create_experiment_metadata(experiment_id, json, apikey=self.apikey)
        metadata_raw = results['data']
        self.assertIsNotNone(metadata_raw)
        self.assertIsNotNone(metadata_raw['experiment_id'])
        self.assertEqual(metadata_raw['experiment_id'], experiment_id)
        self.assertEqual(metadata_raw['owner'], self.user)

    def test_get_experiment_metadata_raw(self):
        fake_metadata = _make_reasonable_metadata()
        self.assertIsNotNone(fake_metadata)
        experiment_id = self.experiment_id
        json = fake_metadata
        results = api.create_experiment_metadata(experiment_id, json, apikey=self.apikey)
        metadata_raw = results['data']
        self.assertIsNotNone(metadata_raw)
        self.assertIsNotNone(metadata_raw['experiment_id'])
        self.assertEqual(metadata_raw['experiment_id'], experiment_id)
        self.assertEqual(metadata_raw['owner'], self.user)
        metadata_id = metadata_raw['id']
        self.assertIsNotNone(metadata_id)
        results = api.get_experiment_metadata(metadata_id, apikey=self.apikey)
        metadata_raw = results['data']
        self.assertIsNotNone(metadata_raw)
        self.assertIsNotNone(metadata_raw['experiment_id'])
        self.assertEqual(metadata_raw['id'], metadata_id)

    def test_get_metadata_by_id(self):
        fake_metadata = _make_reasonable_metadata()
        self.assertIsNotNone(fake_metadata)
        experiment_id = self.experiment_id
        json = fake_metadata
        results = api.create_experiment_metadata(experiment_id, json, apikey=self.apikey)
        metadata_raw = results['data']
        self.assertIsNotNone(metadata_raw)
        self.assertIsNotNone(metadata_raw['experiment_id'])
        self.assertEqual(metadata_raw['experiment_id'], experiment_id)
        self.assertEqual(metadata_raw['owner'], self.user)
        metadata_id = metadata_raw['id']
        self.assertIsNotNone(metadata_id)
        results = api.get_experiment_metadata_by_experiment_id(experiment_id, apikey=self.apikey)
        metadata_raw = results['data']
        self.assertIsNotNone(metadata_raw)
        self.assertIsNotNone(metadata_raw['experiment_id'])
        self.assertEqual(metadata_raw['experiment_id'], experiment_id)
        self.assertEqual(metadata_raw['id'], metadata_id)

    def test_update_metadata(self):
        fake_metadata = _make_reasonable_metadata()
        self.assertIsNotNone(fake_metadata)
        experiment_id = self.experiment_id
        json = fake_metadata
        results = api.create_experiment_metadata(experiment_id, json, apikey=self.apikey)
        metadata_raw = results['data']
        self.assertIsNotNone(metadata_raw)
        self.assertIsNotNone(metadata_raw['experiment_id'])
        self.assertEqual(metadata_raw['experiment_id'], experiment_id)
        self.assertEqual(metadata_raw['owner'], self.user)
        metadata_id = metadata_raw['id']
        self.assertIsNotNone(metadata_id)
        original_path = "/Users/weymouth/Desktop/test/data"
        altered_path = "/Users/weymouth/Desktop/test/alternate_data"
        self.assertEqual(metadata_raw['json']["input_data_dir_path"], original_path)
        altered_metadata = _make_reasonable_metadata()
        altered_metadata["input_data_dir_path"] = altered_path
        results = api.update_experiment_metadata(metadata_id, altered_metadata, apikey=self.apikey)
        metadata_raw = results['data']
        self.assertIsNotNone(metadata_raw)
        self.assertIsNotNone(metadata_raw['experiment_id'])
        self.assertEqual(metadata_raw['experiment_id'], experiment_id)
        self.assertEqual(metadata_raw['id'], metadata_id)
        self.assertEqual(metadata_raw['json']["input_data_dir_path"], altered_path)

    def test_delete_metadata(self):
        fake_metadata = _make_reasonable_metadata()
        self.assertIsNotNone(fake_metadata)
        experiment_id = self.experiment_id
        json = fake_metadata
        results = api.create_experiment_metadata(experiment_id, json, apikey=self.apikey)
        metadata_raw = results['data']
        self.assertIsNotNone(metadata_raw)
        self.assertIsNotNone(metadata_raw['experiment_id'])
        self.assertEqual(metadata_raw['experiment_id'], experiment_id)
        self.assertEqual(metadata_raw['owner'], self.user)
        metadata_id = metadata_raw['id']
        self.assertIsNotNone(metadata_id)
        results = api.delete_experiment_metadata(metadata_id, apikey=self.apikey)
        self.assertTrue(results)
        results = api.get_experiment_metadata(metadata_id, apikey=self.apikey)
        expected = results['error']
        self.assertIsNotNone(expected)
        self.assertIn(metadata_id, expected)


def _make_reasonable_metadata():
    return {
          "time_stamp": "Thu Feb  8 08:36:34 2018",
          "process_metadata": [
            {
              "id": "8da4f353-9076-4796-a51e-7c521772ae51",
              "name": "Create Samples",
              "template": "global_Create Samples",
              "start_row": 5,
              "end_row": 6,
              "start_col": 1,
              "end_col": 2
            },
            {
              "id": "22b1aaaf-2076-44e1-9ace-8d7fe9791c94",
              "name": "Create Samples",
              "template": "global_Create Samples",
              "start_row": 6,
              "end_row": 7,
              "start_col": 1,
              "end_col": 2
            },
            {
              "id": "7f2fb980-809c-4486-95e3-8ec452bfa751",
              "name": "Create Samples",
              "template": "global_Create Samples",
              "start_row": 7,
              "end_row": 8,
              "start_col": 1,
              "end_col": 2
            },
            {
              "id": "92417fe4-1aa4-4494-8967-13f8cc4f6025",
              "name": "Create Samples",
              "template": "global_Create Samples",
              "start_row": 8,
              "end_row": 9,
              "start_col": 1,
              "end_col": 2
            },
            {
              "id": "d7c0f921-6695-4e17-b02e-f5eb37345677",
              "name": "Preperation 1",
              "template": "global_Heat Treatment",
              "start_row": 5,
              "end_row": 6,
              "start_col": 2,
              "end_col": 5
            },
            {
              "id": "566ac438-c2a0-4b31-a9aa-c59c548082df",
              "name": "Preperation 1",
              "template": "global_Heat Treatment",
              "start_row": 6,
              "end_row": 7,
              "start_col": 2,
              "end_col": 5
            },
            {
              "id": "687d94be-5fd7-4fd0-97d7-e61275897131",
              "name": "Preperation 1",
              "template": "global_Heat Treatment",
              "start_row": 7,
              "end_row": 8,
              "start_col": 2,
              "end_col": 5
            },
            {
              "id": "9335c438-650a-4de6-afc0-02e2f0048965",
              "name": "Preperation 1",
              "template": "global_Heat Treatment",
              "start_row": 8,
              "end_row": 9,
              "start_col": 2,
              "end_col": 5
            }
          ],
          "input_excel_file_path": "/Users/weymouth/Desktop/test/short.xlsx",
          "input_data_dir_path": "/Users/weymouth/Desktop/test/data",
          "output_json_file_path": "/Users/weymouth/Desktop/test/metadata.json",
          "project_id": "8197c346-dfdf-4160-8fd1-677f0c8d2d0f",
          "experiment_id": "9fa0dc7e-c503-41a5-8f0b-e5884ec8ae0f",
          "header_row_end": 5,
          "data_row_start": 5,
          "data_row_end": 9,
          "data_col_start": 1,
          "data_col_end": 5,
          "start_attribute_row": 1,
          "sheet_headers": [
            [
              "PROJ: Generic Testing",
              "PROC: Create Samples",
              "PROC: Heat Treatment",
              None,
              None
            ],
            [
              "EXP: Test1",
              "SAMPLES",
              "PARAM",
              "PARAM",
              "FILES"
            ],
            [
              None,
              None,
              "Temperature (C)",
              "Time (h)",
              None
            ],
            [
              "NAME",
              None,
              "Preperation 1",
              None,
              None
            ],
            [
              "LABEL",
              "Sample Name",
              "Temp (\u00baC)",
              "Time (hr)",
              None
            ]
          ],
          "project": None,
          "experiment": None,
          "process_table": None
        }