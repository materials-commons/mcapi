import unittest
from random import randint
from mcapi import set_remote_config_url, get_remote_config_url, get_all_templates

url = 'http://mctest.localhost/api'

class TestTempletAccess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)

    def test_all_templets(self):
        self.assertEqual(get_remote_config_url(), url)
        templates = get_all_templates()
        self.assertIsNotNone(templates)
        self.assertTrue(len(templates) > 0)
        self.assertTrue(templates[0].otype == 'template')
        table = self.make_template_table(templates)
        probe = table['global_Electropolishing']
        self.assertIsNotNone(probe)
        self.assertTrue(probe.otype == 'template')

    def make_template_table(self,templates):
        ret = {}
        for t in templates:
            ret[t.id] = t
        return ret

