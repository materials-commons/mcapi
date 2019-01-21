import unittest
import os
import re
import materials_commons.api as mcapi
import json
from materials_commons.api import Template
from .cli_test_functions import working_dir, captured_output, print_string_io
from materials_commons.cli.init import init_subcommand
from materials_commons.cli.samp import SampSubcommand
from materials_commons.cli.functions import make_local_project, make_local_expt, set_current_experiment


def mkdir_if(path):
    if not os.path.exists(path):
        os.mkdir(path)


def remove_if(path):
    if os.path.exists(path):
        os.remove(path)


def rmdir_if(path):
    if os.path.exists(path):
        os.rmdir(path)


def make_file(path, text):
    with open(path, 'w') as f:
        f.write(text)


class TestMCProc(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if 'TEST_DATA_DIR' not in os.environ:
            raise Exception("No TEST_DATA_DIR environment variable")
        cls.cli_test_project_path = os.path.join(os.environ['TEST_DATA_DIR'], 'cli_test_project')
        cls.proj_path = os.path.join(cls.cli_test_project_path, 'CLITest')
        cls.clean()
        cls.init()

    @classmethod
    def init(cls):
        mkdir_if(cls.cli_test_project_path)
        mkdir_if(cls.proj_path)
        testargs = ['mc', 'init']
        with captured_output(wd=cls.proj_path) as (sout, serr):
            init_subcommand(testargs)
        # print_stringIO(sout)
        out = sout.getvalue().splitlines()

        cls.make_samples()

    @classmethod
    def clean_files(cls):
        mc = os.path.join(cls.proj_path, ".mc")
        config = os.path.join(mc, "config.json")
        remove_if(config)
        rmdir_if(mc)
        rmdir_if(cls.proj_path)

    @classmethod
    def clean_proj(cls):
        proj_list = mcapi.get_all_projects()
        proj_dict = {p.name: p for p in proj_list}
        if 'CLITest' in proj_dict:
            proj_dict['CLITest'].delete()

    @classmethod
    def clean(cls):
        cls.clean_files()
        cls.clean_proj()

    @classmethod
    def make_samples(cls):
        proj = cls.get_proj()
        expt = proj.create_experiment("TestExptName", "TestExptDesc")
        set_current_experiment(proj, expt)

        cls.proc = []
        cls.samp = []
        for proc_index in range(3):
            proc = expt.create_process_from_template(Template.create)
            sample_names = ["Sample " + str(i) + " from Proc " + str(proc_index) for i in range(3)]
            samples = proc.create_samples(sample_names)
            proc.add_number_measurement("count", 6.7)
            cls.proc.append(proc)
            cls.samp += samples

    @classmethod
    def remove_samples(cls):
        proj = cls.get_proj()
        expt = make_local_expt(proj)
        expt.delete(dry_run=False, delete_processes_and_samples=True)

    @classmethod
    def get_proj(cls):
        return make_local_project(cls.proj_path)

    def test_samp_list(self):
        samp_subcommand = SampSubcommand()

        # list samples
        testargs = ['mc', 'samp']
        with captured_output(wd=self.proj_path) as (sout, serr):
            samp_subcommand(testargs)
        # print_stringIO(sout)
        self.assertTrue(True)

    def test_samp_list_names(self):
        samp_subcommand = SampSubcommand()

        # list samples
        testargs = ['mc', 'samp'] + [samp.name for samp in self.samp]
        with captured_output(wd=self.proj_path) as (sout, serr):
            samp_subcommand(testargs)
        # print_stringIO(sout)
        self.assertTrue(True)

    def test_samp_list_ids(self):
        samp_subcommand = SampSubcommand()

        # list samples
        testargs = ['mc', 'samp', '--id'] + [samp.id for samp in self.samp]
        with captured_output(wd=self.proj_path) as (sout, serr):
            samp_subcommand(testargs)
        # print_stringIO(sout)
        self.assertTrue(True)

    def test_samp_json(self):
        samp_subcommand = SampSubcommand()

        # print() sample JSON data
        testargs = ['mc', 'samp', '--json']
        with captured_output(wd=self.proj_path) as (sout, serr):
            samp_subcommand(testargs)
        # print_stringIO(sout)
        data = json.loads(sout.getvalue())
        self.assertTrue(True)

    def test_samp_details(self):
        samp_subcommand = SampSubcommand()

        # print() sample details
        testargs = ['mc', 'samp', '--details']
        with captured_output(wd=self.proj_path) as (sout, serr):
            samp_subcommand(testargs)
        # print_stringIO(sout)
        self.assertTrue(True)

    @classmethod
    def tearDownClass(cls):
        cls.clean()
