import unittest
import os
import re
from .cli_test_functions import captured_output
from .cli_test_exceptions import MCCLITestException


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

def test_project_directory():
    if 'MC_TEST_DATA_DIR' not in os.environ:
        raise Exception("No MC_TEST_DATA_DIR environment variable")
    return os.environ['MC_TEST_DATA_DIR']

def basic_project_1(path):
    """Construct a basic TestProject, example #1 (two levels of directories, each with two files)

    Arguments
    ---------
    path: str, path where test project directory should be created. Does not need to already exist.
    """
    dirs = [
        os.path.join(path, "level_1"),
        os.path.join(path, "level_1", "level_2")
    ]
    files = [
        (os.path.join(path, "file_A.txt"), "This is file A, level 0"),
        (os.path.join(path, "file_B.txt"), "This is file B, level 0"),
        (os.path.join(path, "level_1", "file_A.txt"), "This is file A, level 1"),
        (os.path.join(path, "level_1", "file_B.txt"), "This is file B, level 1"),
        (os.path.join(path, "level_1", "level_2", "file_A.txt"), "This is file A, level 2"),
        (os.path.join(path, "level_1", "level_2", "file_B.txt"), "This is file B, level 2")
    ]
    return TestProject(path, dirs, files)

class TestProject(object):
    """Create and clean a local test directory with files and sub-directories

    Must be named ".../__clitest__<something>"
    """

    def __init__(self, path, dirs, files):
        self.path = path
        self.dirs = dirs
        self.files = files
        self.project_name = os.path.basename(self.path)
        self.parent_path = os.path.dirname(self.path)

        if self.project_name[:11] != "__clitest__":
            raise MCCLITestException("Invalid test project name: ", self.project_name)

        # make project top level directory, raises (?) if self.parent_path does not exist
        mkdir_if(self.path)

        # make local files and directories listed in self.files and self.dirs
        self.make_test_files()

    def clean_files(self):
        self.remove_test_files()
        mc = os.path.join(self.path, ".mc")
        config = os.path.join(mc, "config.json")
        remove_if(config)
        rmdir_if(mc)
        rmdir_if(self.path)

    def make_test_files(self):
        """Make local files and directories listed in self.files and self.dirs"""
        for dir in self.dirs:
            mkdir_if(dir)
        for val in self.files:
            make_file(val[0], val[1])

    def remove_test_files(self):
        """Remove local files and directories listed in self.files and self.dirs"""
        for val in self.files:
            remove_if(val[0])
        for dir in reversed(self.dirs):
            rmdir_if(dir)

# def init_remote_only_test_project(test_project):
#     """Create a remote-only test project
#
#     Arguments
#     ---------
#     test_project: TestProject, Test project to create locally, init mc project, upload files, then
#         delete local files and sub-directories, so that a test can begin as if the local project
#         does not exist.
#     """
#     mkdir_if(test_project.path)
#     testargs = ['mc', 'init']
#     with captured_output(wd=test_project.path) as (sout, serr):
#         init_subcommand(testargs)
#     # print_stringIO(sout)
#     # out = sout.getvalue().splitlines()
#
#     self.make_test_files()
#
#     testargs = ['mc', 'up', '-r', '.']
#     with captured_output(wd=test_project.path) as (sout, serr):
#         up_subcommand(testargs)
#
#     self.remove_test_files()
#     remove_if(os.path.join(test_project.path, ".mc", "config.json"))
#     remove_if(os.path.join(test_project.path, ".mc", "project.db"))
#     remove_if(os.path.join(test_project.path, ".mc"))
#     rmdir_if(test_project.path)

# def clean_test_project(cls):
#     """Remove local files and directories listed in self.files and self.dirs"""
#     # must update: proj_list = mcapi.get_all_projects()
#     proj_dict = {p.name: p for p in proj_list}
#     if self.project_name in proj_dict:
#         proj_dict[self.project_name].delete()

# @classmethod
# def clean(cls):
#     cls.clean_proj()
#     cls.clean_files()
