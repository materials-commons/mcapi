from os import path as os_path
import demo_project as demo


local_example_data_path = './example_data/data_for_full_demo_project'
project_data_path = os_path.abspath(local_example_data_path)

print "Creating demo project with data from: " + project_data_path

builder = demo.DemoProject(project_data_path)

project = builder.build_project()

new_project_name = "My demo Project"
new_project_description = "A demo project build from a script"

project = project.rename(new_project_name, new_project_description)

print "Created demo project with name = " + project.name
