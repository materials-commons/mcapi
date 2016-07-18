import mcapi, os

# list local projects
print "\nLocal projects:"
locals = mcapi.list_projects(remote=None)
for p in locals:
  print "\n", p['name']
  for key, val in p.iteritems():
    print "  ", key, ":", val
  
print "\n\nRemote projects:"
remotes = mcapi.list_projects(mcapi.mcorg())
# list remote projects
for p in remotes:
  print "\n", p['name']
  for key, val in p.iteritems():
    print "  ", key, ":", val
  
## get all Projects
#all_proj = mcapi.get_projects()
#
#print "All projects:"
#for p in all_proj:
#  print " ", p.name
#
# get a Project by id
print ""
proj = mcapi.Project(id=remotes[1]['id'])
print "Get Project by id:", remotes[1]['id']
print "  name:", proj.name, "  id:", proj.id

## get a Project by name
#print ""
#proj = mcapi.get_project_by_name(all_proj[0].name)
#print "Get Project by name:", all_proj[0].name
#print "  name:", proj.name, "  id:", proj.id
#
## get a Project by wrong name raises ValueError
#print ""
#try:
#  proj = mcapi.get_project_by_name("WrongProjectName")
#  print "Get Project by name:", "WrongProjectName"
#  print "  name:", proj.name, "  id:", proj.id
#except ValueError as e:
#  print "ValueError:", e
#

# get datafiles from a Project
print ""
for root, dirs, files in proj.top.walk():
  print root.path, root.id
  print "  dirs:" 
  for d in dirs:
    print "    ", d.name, d.path, d.localpath
  print "  files:"
  for f in files:
    print "    ", f.name, f.path, f.localpath
      




