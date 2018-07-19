import unittest
from materials_commons.api import api


class TestTemplatesRaw(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "another@test.mc"
        cls.apikey = "another-bogus-account"

    def test_get_all_templates_raw(self):
        template_list = api.get_all_templates(apikey=self.apikey)
        found = None
        for template in template_list:
            if template['id'] == 'global_Create Samples':
                found = template
        self.assertIsNotNone(found)
