import unittest
from os.path import join, exists
from os import mkdir
import shutil, os
import mcapi
import fixtures

def get_id(name, projs):
  res = [p["id"] for p in projs if p["name"] == name]
  if len(res):
    return res[0]
  else:
    return None
      

class TestProject(unittest.TestCase):
  
  def setUp(self):
    """
    Read test case data
    """
    print ""
    self.remote = mcapi.Remote({'mcurl':'http://mctest.localhost/api'})
    self.cases = fixtures.read_test_cases("test_project")["project"]
    self._verbose = False
    print "using:", self.remote.mcurl
  
  def clear_tmp(self):
    # clear 'tmp' directory
    if exists(fixtures.tmp_dir):
      shutil.rmtree(fixtures.tmp_dir)
    mkdir(fixtures.tmp_dir)
  
  def clear_local_projects(self):
    # checking if test projects already exist locally
    projs = mcapi.list_projects(self.remote)
    for case in self.cases["project"]:
      id = get_id(case["proj"], projs)
      if id is not None:
        proj = mcapi.Project(id=id)
        if proj.localpath is not None:
          mcapi.delete_project(proj)
    
  def test_list_projects(self):
    """
    Test mcapi.project.list_projects
    """
    projs = mcapi.list_projects(self.remote)
    self.assertTrue(len(projs))
  
  def test_project(self):
    """
    Test mcapi.project
    """
    cases = self.cases["project"]
    
    # test creating, deleting project by localpath
    # test creating Project object by localpath
    self.clear_local_projects()
    for case in cases:
      projname = case["proj"]
      localpath = join(fixtures.projects_dir, projname)
      
      mcapi.create_project(projname, localpath, upload=True, verbose=self._verbose)
      proj = mcapi.Project(localpath=localpath)
      mcapi.delete_project(proj)
    
    # test if project is listed
    # test creating Project instance by id and cloning
    self.clear_tmp()
    projs = mcapi.list_projects(self.remote)
    for case in cases:
      projname = case["proj"]
      localpath = join(fixtures.tmp_dir, projname)
      
      # clone project, with download
      proj = mcapi.Project(id=get_id(projname, projs))
      mkdir(localpath)
      proj, status = mcapi.clone_project(proj, localpath, download=True, verbose=self._verbose)
      
      # check that one downloaded directory / file exists
      dirname = join(localpath,"dir_1")
      self.assertTrue(exists(dirname))
      self.assertTrue(exists(join(dirname,"file1.txt")))
      
      if self._verbose:
        print status.out
      
      mcapi.delete_project(proj)
      
    # test individual file download
    self.clear_tmp()
    for case in cases:
      # get a Project
      projname = case["proj"]
      projdir = join(fixtures.tmp_dir, projname)
      proj = mcapi.Project(id=get_id(projname, projs))
      
      # clone Project
      mkdir(projdir)
      proj, status = mcapi.clone_project(proj, projdir, verbose=self._verbose)
      
      if not status:
        raise Exception("Error cloning project: " + projdir)
      
      if self._verbose:
        print status.out
      
      # download file-by-file
      for root, dirs, files in proj.top.walk():
        for f in files:
          status = f.download()
          self.assertTrue(status)
          self.assertTrue(exists(f.localpath))
          if self._verbose:
            print status.out
    
    # test individual file upload
    for case in cases:
      # get a Project
      projname = case["proj"]
      projdir = join(fixtures.tmp_dir, projname)
      proj = mcapi.Project(localpath=projdir)
      
      # upload file-by-file
      for root, dirs, files in proj.top.walk():
        for f in files:
          status = f.upload()
          self.assertTrue(status)
          if self._verbose:
            print status.out
      
      # upload by directory
      for root, dirs, files in proj.top.walk():
        for d in dirs:
          status = d.upload()
          self.assertTrue(status)
          if self._verbose:
            print status.out
    
    #clean up
    self.clear_tmp()
  
  def test_project_walk(self):
    projs = mcapi.list_projects(self.remote)
    
    # walk 3 projects with 1 dir & 1 file (if possible)
    N_proj = 0
    for p in projs:
      proj = mcapi.Project(id=p["id"])
      N_file = 0
      N_dir = 0
      for root, dirs, files in proj.top.walk():
        for d in dirs:
          N_dir += 1
        for f in files:
          N_file += 1
        if N_dir > 1 and N_file > 1:
          N_proj += 1
      if N_proj > 2:
        break
    
    # completed
    self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()