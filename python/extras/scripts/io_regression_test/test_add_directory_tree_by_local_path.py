#!/usr/bin/env python

from materials_commons.api import get_all_projects
import os

project_name = "File Test"
base_path = "/Volumes/Data2/GlobusEndpoint/mc-base/transfer-test-transfer-1530295080814"

found_project = None
for project in get_all_projects():
    if project.name == project_name:
        found_project = project

if not found_project:
    print("Did not find project with name = {}".format(project_name))
    exit(-1)

project = found_project
print("Using project: {} ({})".format(project.name, project.id))

current_directory = os.getcwd()
os.chdir(base_path)

directory = project.get_top_directory()

for f_or_d in os.listdir('.'):
    if os.path.isfile(f_or_d):
        directory.add_file(str(f_or_d), str(f_or_d), True)
    if os.path.isdir(f_or_d):
        directory.add_directory_tree(str(f_or_d), '.', True)

os.chdir(current_directory)

