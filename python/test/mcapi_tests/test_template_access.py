import unittest
import pytest
from random import randint
from mcapi import set_remote_config_url, get_remote_config_url, get_all_templates
from mcapi import get_all_users, _create_new_tamplate, _update_template

url = 'http://mctest.localhost/api'


def fake_name(prefix):
    number = "%05d" % randint(0, 99999)
    return prefix+number


class TestTemplateAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_remote_config_url(url)
        user_id = "test@test.mc"
        users = get_all_users()
        user = None
        for probe in users:
            if probe.id == user_id:
                user = probe
        cls.test_user_id = user_id
        cls.test_user = user

    def test_is_setup_correctly(self):
        self.assertIsNotNone(self.test_user)
        self.assertEqual(self.test_user_id,self.test_user.id)

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

    def test_can_create(self):
        test_name = fake_name('test-template')
        test_id = "global_" + test_name
        template_data = self.make_template_data(test_name)
        template = _create_new_tamplate(template_data)
        self.assertIsNotNone(template)
        self.assertEqual(template.id,test_id)
        self.assertEqual(template.otype,'template')
        self.assertFalse(template.does_transform)

    def test_cannot_create_twice(self):
        test_name = fake_name('test-template')
        test_id = "global_" + test_name
        template_data = self.make_template_data(test_name)
        template = _create_new_tamplate(template_data)
        self.assertIsNotNone(template)
        self.assertEqual(template.id, test_id)
        self.assertEqual(template.otype, 'template')
        self.assertFalse(template.does_transform)

        with pytest.raises(Exception):
            _create_new_tamplate(template_data)

    def test_can_update(self):
        test_name = fake_name('test-template')
        test_id = "global_" + test_name
        template_data = self.make_template_data(test_name)
        template = _create_new_tamplate(template_data)
        self.assertIsNotNone(template)
        self.assertEqual(template.id,test_id)
        self.assertEqual(template.otype,'template')
        self.assertFalse(template.does_transform)
        self.assertEqual(template.owner, 'test@test.mc')

        update_data = template.input_data
        update_data["does_transform"] = True
        self.assertEqual(update_data['owner'],'test@test.mc')
        update_data.pop('id')

        template = _update_template(template.id,update_data)
        self.assertIsNotNone(template)
        self.assertEqual(template.id,test_id)
        self.assertEqual(template.otype,'template')
        self.assertTrue(template.does_transform)

    def make_template_table(self, templates):
        ret = {}
        for t in templates:
            ret[t.id] = t
        return ret

    def make_template_data(self, test_name):
        data =    \
            {
                "category": "",
                "description": "As Measured",
                "destructive": False,
                "does_transform": False,
                "measurements": [],
                "name": test_name,
                "otype": "template",
                "process_name": "Test Template Process",
                "process_type": "test",
                "setup": [
                    {
                        "attribute": "instrument",
                        "name": "Instrument",
                        "properties": []
                    }
                ]
            }

        return data
