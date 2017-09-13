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
        print(dataset)
        self.assertFalse('x')