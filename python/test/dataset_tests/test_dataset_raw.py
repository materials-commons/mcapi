import unittest
import pytest

from dataset import Public


class TestDatasetRaw(unittest.TestCase):
    def test_form_url(self):
        public = Public()
        probe_url = public.make_url(Public.path_for_dateaset_id + "testing")
        self.assertEqual(probe_url, Public.default_base_url + Public.path_for_dateaset_id + "testing")

    def test_get_public_dataset(self):
        id = "57490e70-df32-4592-8a6f-8a6cfbd36174"
        public = Public()
        probe_url = public.make_url(Public.path_for_dateaset_id + id)
        self.assertEqual(probe_url, Public.default_base_url + Public.path_for_dateaset_id + id)
        dataset = public.get_dataset(id)
        self.assertIsNotNone(dataset)
        self.assertIsNotNone(dataset.raw_data)
        self.assertEqual(dataset.raw_data['id'],id)


class TestDatasetApptributes(unittest.TestCase):
    def test_attributes(self):
        id = "57490e70-df32-4592-8a6f-8a6cfbd36174"
        public = Public()
        dataset = public.get_dataset(id)
        self.assertIsNotNone(dataset)
        print("--")
        # 'authors' - list
        print(dataset.authors)
        # 'birthtime' - string date
        # 'description' - string
        self.assertEqual(dataset.doi,"")
        # 'embargo_date' - string date
        # 'files' - list
        self.assertTrue(dataset.funding.startswith("Department of Energy"))
        self.assertEqual(dataset.id, id)
        self.assertTrue(dataset.institution.startswith("University of Michigan"))
        # 'keywords' - list
        # 'license' - dict
        # 'mtime' - string date
        # 'other_datasets' - list
        self.assertEqual(dataset.owner, 'tradiasa@umich.edu')
        # 'papers'
        # 'processes'
        self.assertTrue(dataset.published)
        # 'published_date' - string data
        # 'publisher'
        self.assertEqual(dataset.publisher, "Tracy Berman")
        # 'samples' - list
        # 'tags' - list
        self.assertEqual(dataset.title, "Microsegregation & Microstructure in HPDC AM Series Alloys")
        # 'zip' - dict
