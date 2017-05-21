import unittest
import os
import re
import mcapi
from mcapi import Template
from cli_test_functions import working_dir, captured_output, print_stringIO
from mcapi.cli.init import init_subcommand
from mcapi.cli.proc import ProcSubcommand
from mcapi.cli.functions import make_local_project, set_current_experiment

url = 'http://mctest.localhost/api'

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
        mcapi.set_remote_config_url(url)
        if not 'TEST_DATA_DIR' in os.environ:
            raise Exception("No TEST_DATA_DIR environment variable")
        cls.cli_test_project_path = os.path.join(os.environ['TEST_DATA_DIR'], 'cli_test_project')
        cls.proj_path = os.path.join(cls.cli_test_project_path, 'CLITest')
        
    
    @classmethod
    def init(cls):
        mkdir_if(cls.cli_test_project_path)
        mkdir_if(cls.proj_path)
        testargs = ['mc', 'init']
        with captured_output(wd=cls.proj_path) as (sout, serr):
            init_subcommand(testargs)
        #print_stringIO(sout)
        out = sout.getvalue().splitlines()
        
        cls.make_processes()
        
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
        proj_dict = {p.name:p for p in proj_list}
        if 'CLITest' in proj_dict:
            proj_dict['CLITest'].delete()

    @classmethod
    def clean(cls):
        cls.clean_files()
        cls.clean_proj()
    
    @classmethod
    def make_processes(cls):
        proj = cls.get_proj()
        expt = proj.create_experiment("TestExptName", "TestExptDesc")
        set_current_experiment(proj, expt)
        
        cls.proc = []
        cls.proc.append(expt.create_process_from_template(Template.create))
        cls.proc.append(expt.create_process_from_template(Template.create))
    
    @classmethod
    def remove_processes(cls):
        proj = cls.get_proj()
        expt = make_local_expt(proj)
        expt.delete(dry_run=False, delete_processes_and_samples=True)
    
    def setUp(self):
        self.clean()
        self.init()
    
    def tearDown(self):
        self.clean()
    
    @classmethod
    def get_proj(cls):
        return make_local_project(cls.proj_path)

    def test_proc_list(self):
        proc_subcommand = ProcSubcommand()
        
        # ls 1 file (in top directory)
        testargs = ['mc', 'proc']
        with captured_output(wd=self.proj_path) as (sout, serr):
            proc_subcommand(testargs)
        print_stringIO(sout)
        self.assertTrue(True)
    
    @classmethod
    def tearDownClass(cls):
        cls.clean()
        
            
