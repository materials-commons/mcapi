from mcapi import get_all_projects
import sys

if len(sys.argv) < 2:
    print "supply project_id as command line argument"
    sys.exit(1)

project_id = sys.argv[1]

found_project = None

for project in get_all_projects():
    if project.id == project_id:
        found_project = project

if found_project:
    project = found_project
    print "deleting project: " + project.name + "..."
    project.delete()
    print "done."
else:
    print "no project found: " + project_id