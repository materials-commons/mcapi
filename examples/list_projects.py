import mcapi, os

# load APIKey
mcapi.init()

# get all Projects
all_proj = mcapi.get_projects()

print "All projects:"
for p in all_proj:
  print " ", p.name

# get a Project by id
print ""
proj = mcapi.get_project(all_proj[0].id)
print "Get Project by id:", all_proj[0].id
print "  name:", proj.name, "  id:", proj.id

# get a Project by name
print ""
proj = mcapi.get_project_by_name(all_proj[0].name)
print "Get Project by name:", all_proj[0].name
print "  name:", proj.name, "  id:", proj.id

# get a Project by wrong name raises ValueError
print ""
try:
  proj = mcapi.get_project_by_name("WrongProjectName")
  print "Get Project by name:", "WrongProjectName"
  print "  name:", proj.name, "  id:", proj.id
except ValueError as e:
  print "ValueError:", e

# get datafiles from a Project
print ""
for p in all_proj:
  print ""
  for root, dirs, files in p.walk():
    print root.path, [f.name for f in files]
