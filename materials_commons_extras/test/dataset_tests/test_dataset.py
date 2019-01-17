import unittest
import pytest

from ..dataset.public_connection import Public


class TestDatasetRaw(unittest.TestCase):
    @pytest.mark.skip(reason="test immature - requires hard coded id value")
    def test_form_url(self):
        public = Public()
        probe_url = public.make_url(Public.path_for_dataset_id + "testing")
        self.assertEqual(probe_url, Public.default_base_url + Public.path_for_dataset_id + "testing")

    @pytest.mark.skip(reason="test immature - requires hard coded id value")
    def test_get_public_dataset(self):
        id = "57490e70-df32-4592-8a6f-8a6cfbd36174"
        public = Public()
        probe_url = public.make_url(Public.path_for_dataset_id + id)
        self.assertEqual(probe_url, Public.default_base_url + Public.path_for_dataset_id + id)
        dataset = public.get_dataset(id)
        self.assertIsNotNone(dataset)
        self.assertIsNotNone(dataset.raw_data)
        self.assertEqual(dataset.raw_data['id'], id)


class TestDatasetAttributes(unittest.TestCase):
    @pytest.mark.skip(reason="test immature - requires hard coded id value")
    def test_attributes(self):
        id = "57490e70-df32-4592-8a6f-8a6cfbd36174"
        public = Public()
        dataset = public.get_dataset(id)
        self.assertIsNotNone(dataset)
        authors = dataset.authors
        self.assertIsNotNone(authors)
        self.assertEqual(len(authors), 4)
        berman = authors[0]
        self.assertEqual(berman.lastname, 'Berman')
        self.assertTrue('microstructure and microsegregation' in dataset.description)
        self.assertEqual(dataset.doi, "")
        files = dataset.files
        self.assertEqual(len(files), 440)
        self.assertEqual(files[0].name, 'epma_run20150608.xlsx')
        self.assertTrue(dataset.funding.startswith("Department of Energy"))
        self.assertEqual(dataset.id, id)
        self.assertTrue(dataset.institution.startswith("University of Michigan"))
        self.assertTrue('opendatacommons' in dataset.license.link)
        self.assertTrue('Attribution' in dataset.license.name)
        self.assertEqual(dataset.owner, 'tradiasa@umich.edu')
        self.assertEqual(len(dataset.processes), 95)
        self.assertEqual(dataset.processes[0].name, "SEM")
        self.assertTrue(dataset.published)
        self.assertEqual(dataset.publisher, "Tracy Berman")
        self.assertEqual(dataset.title, "Microsegregation & Microstructure in HPDC AM Series Alloys")
        self.assertEqual(dataset.zip.filename, 'Microsegregation_&_Microstructure_in_HPDC_AM_Series_Alloys.zip')
        self.assertEqual(len(dataset.samples), 8)
        self.assertEqual(dataset.samples[0].name, "AM40-2p5-F")
