import unittest
import string
import json
from .cli_test_functions import captured_output, print_string_io
from materials_commons.cli.templates import TemplatesSubcommand


class TestMCTemplates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.templates_subcommand = TemplatesSubcommand()

    def test_mc_templates_all(self):
        testargs = ['mc', 'templates']
        with captured_output() as (sout, serr):
            self.templates_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()

        headers = out[0].split()
        self.assertEqual(headers[0], "name")
        self.assertEqual(headers[1], "id")

        name = [x.split("global_")[0].strip() for x in out if "global_" in x]
        id = [x.split("global_")[1].strip() for x in out if "global_" in x]

        for n in name:
            self.assertEqual(name.index(n), id.index(n))

    def test_mc_templates_all_json(self):
        testargs = ['mc', 'templates', '--json']
        with captured_output() as (sout, serr):
            self.templates_subcommand(testargs)
        # print_stringIO(sout)
        data = json.loads(sout.getvalue())
        self.assertTrue(True)

    def test_mc_templates_by_name(self):
        testargs = ['mc', 'templates', 'Create Samples']
        with captured_output() as (sout, serr):
            self.templates_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()
        self.assertTrue(True)

    def test_mc_templates_by_name_json(self):
        testargs = ['mc', 'templates', '--json', 'Create Samples']
        with captured_output() as (sout, serr):
            self.templates_subcommand(testargs)
        # print_stringIO(sout)
        template = json.loads(sout.getvalue())
        self.assertTrue(True)

    def test_mc_templates_by_id(self):
        testargs = ['mc', 'templates', '--id', 'global_Create Samples']
        with captured_output() as (sout, serr):
            self.templates_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()
        err = serr.getvalue().splitlines()
        self.assertTrue(True)

    def test_mc_templates_by_id_json(self):
        testargs = ['mc', 'templates', '--json', '--id', 'global_Create Samples']
        with captured_output() as (sout, serr):
            self.templates_subcommand(testargs)
        # 2print_stringIO(sout)
        template = json.loads(sout.getvalue())
        self.assertTrue(True)
