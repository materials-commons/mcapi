from materials_commons.api import get_all_projects, get_project_by_id

all_projects = get_all_projects()

# Get project - method 1 - by name

project_name = "Demo Project"

demo_project = None
for probe in all_projects:
    if probe.name == project_name:
        demo_project = probe

if not demo_project:
    print("Unable to find 'Demo Project'")
    if len(all_projects) > 0:
        print("Found these projects...")
        for p in all_projects:
            print(" - - - ")
            p.pretty_print()
    else:
        print("found no projects on server")
    print(" - - - ")
    print("Create demo project or use another project")
    print(" - - - ")
    exit(1)

# Get project - method 2 - by id

project_id = demo_project.id
demo_project = get_project_by_id(project_id)

if not demo_project:
    print("Unable to find Project with id = " + project_id)
    exit(1)

# Project
print("")
print("Project ---- ...")
demo_project.pretty_print()

# Experiment in Project
experiments = demo_project.get_all_experiments()
experiment = experiments[0]
print("")
print("Experiment ---- ...")
experiment.pretty_print()

processes = experiment.get_all_processes()
for p in processes:
    print("")
    print("Process ---- ...")
    p.pretty_print()
