import string, sqlite3, json, subprocess
from os import makedirs, remove
from os.path import join, splitext, dirname, basename, exists
from glob import glob

import mcapi.api as api
from mcapi.api import mcdatapath, mcorg, Remote, mccli, set_cli_remote, CLIResult
from mcapi.datadir import Datadir
from mcapi.datafile import Datafile



class Project(api.MCObject):
    """
    Materials Commons Project object.
    
    Attributes
    ----------
    top: mcapi.Datadir
      Top-level Datadir in this Project
    
    remote: mcapi.Remote or None
      Where this is hosted
    
    localpath: str or None
      the path to this project on the local machine. None if unknown or not 
      stored locally.
    """
    
    def __init__(self, localpath=None, id=None, remote=mcorg()):
        """
        Arguments
        ----------
        localpath: str, optional
          the path to the project on the local machine. Initialize with this if 
          the project is stored locally to enable file upload/download.
        
        id: str, optional
          the project id. Initialize with this if the project is not stored locally.
        
        remote: mcapi.mcorg(), optional, default uses https://materialscommons.org
          where the project is hosted
        
        """
        self.remote = remote
        self.localpath = None
        
        projs = list_projects(self.remote)
        if localpath is not None:
            data = filter(lambda p: p['name'] == basename(localpath), projs)[0]
            self.localpath = localpath
        elif id is not None:
            data = filter(lambda p: p['id'] == id, projs)[0]
                  
        super(Project, self).__init__(data)
        
        attr = ['localpath']
        for a in attr:
          setattr(self, a, data.get(a,None)) 
        
#        print "Constructing Project"
#        for k in data.keys():
#          print k
#        print ""
        
        self._top = None
        
        # holds Datadir, using id for key
        self._datadir = dict()
        
        # holds Datafile, using id for key
        self._datafile = dict()
    
    
    def local_to_remote_path(self, localpath):
        return join(self.name, relpath(localpath, self.path))
    
    
    @property
    def top(self):
        if self._top is None:
            data = api.top(self.id, self.remote)
            self._top = Datadir(self, None, data)
        return self._top
    
    
    def datadir(self, key, type='path', create=False):
        """
        Get one Datadir object.
        
        Arguments
        ----------
          key: str
            One of:
              'path': path to directory from (and including) the top-level 
                directory, ex. 'MyProj/path/to/mydir'
              'localpath': path to directory on local machine, 
                 ex. '/some/path/to/MyProj/path/to/mydir'
              'id': Datadir id, ex. '9a9ea9d7-cebf-401f-814c-343693b177f0'
              
          type: str, optional, default='path'
            One of 'path', 'localpath', 'id'
          
          create: boolean, optional, default False
            If type='path' or 'localpath', and create=True, the Datadir
            will be created if it does not already exist; else raise a ValueError.
          
        Returns
        ----------
          datadir: mcapi.Datadir instance
            the Datadir with specified key
        
        """
        if type == 'id':
            return self._datadir_by_id(key)
        elif type == 'localpath':
            return self._datadir_by_localpath(key, create=create)
        elif type == 'path':
            return self._child_by_path(key, crate=create, type='datadir')
        else:
            raise ValueError("type=" + type + ". type must be one of 'id', 'localpath', 'path'")
    
    
    def _datadir_by_id(self, id):
        """
        Return Datadir by id. Ex. '9a9ea9d7-cebf-401f-814c-343693b177f1'
        """
        dir = self._datadir.get(id, None)
        if dir is None:
            data = api.datadir(self.id, id, self.remote)
            parentpath = dirname(data['path'])
            parent = self._child_by_path(parentpath, create=False, type='datadir')
            dir = Datadir(self, parent, data)
            self._datadir[id] = dir
        return dir
    
    
    def _datadir_by_localpath(self, localpath, create=False):
        """
        Return Datadir by local path. Ex. '/some/path/MyProj/path/to/mydir'
        """
        path = self.local_to_remote_path(localpath)
        dir = self._child_by_path(path, create=create, type='datadir')
        return dir
    
    
    def datadirs(self, keys, type='id', create=False):
        """
        Get many Datadir objects.
        
        Arguments
        ----------
          key: iterable of str
            iteratable of one of these types:
              'path': path to directory from (and including) the top-level 
                directory, ex. 'MyProj/path/to/mydir'
              'localpath': path to directory on local machine, 
                 ex. '/some/path/to/MyProj/path/to/mydir'
              'id': Datadir id, ex. '9a9ea9d7-cebf-401f-814c-343693b177f0'
              
          type: str
            One of 'path', 'localpath', 'id' 
          
          create: boolean, optional, default False
            If type='path' or 'localpath', and create=True, the Datadir
            will be created if it does not already exist; else raise a ValueError.
          
        Returns
        ----------
          datadir: List[mcapi.Datadir]
            the Datadir with specified keys
        
        """
        return [self.datadir(key, type='id') for key in keys]
    
       
    def datafile(self, key, type='path', parent=None):
        """
        Get one Datafile object.
        
        Arguments
        ----------
          key: str
            One of:
              'path': path to file from (and including) the top-level 
                directory, ex. 'MyProj/path/to/myfile.ext'
              'localpath': path to file on local machine, 
                 ex. '/some/path/to/MyProj/path/to/myfile.ext'
              'id': Datadir id, ex. 9a9ea9d7-cebf-401f-814c-343693b177f0
              
          type: str, optional, default='path'
            One of 'path', 'localpath', 'id'
          
          parent: mcapi.Datadir, optional
            Required if requesting Datafile by 'id'
          
          create: boolean, optional, default False
            If type='path' or 'localpath', and create=True, the Datadir
            will be created if it does not already exist; else raise a ValueError.
          
        Returns
        ----------
          datafile: mcapi.Datafile
            the Datafile with specified key
        
        """
        if type == 'id':
            return self._datafile_by_id(parent, key)
        elif type == 'localpath':
            return self._datafile_by_localpath(key, create)
        elif type == 'path':
            return self._child_by_path(key, create)
        else:
            raise ValueError("type=" + type + ". type must be one of 'id', 'localpath', 'path'")
    
    
    def _datafile_by_id(self, parent, id):
        file = self._datafile.get(id, None)
        if file is None:
            data = api.datafile(self.id, id, self.remote)
            file = datadir.Datafile(self, parent, data)
            self._datafile[file.id] = file
        return file
    
    
    def _datafile_by_localpath(self, localpath, create=False):
        path = self.local_to_remote_path(localpath)
        dir = self._child_by_path(path, create=create, type='datadir')
        return dir
    
    
    def datafiles(self, keys, type='path', parent=None):
        """
        Get many Datafile objects by id.  
        
        Arguments
        ----------
          key: List[str]
            List of:
              'path': path to file from (and including) the top-level 
                directory, ex. 'MyProj/path/to/myfile.ext'
              'localpath': path to file on local machine, 
                 ex. '/some/path/to/MyProj/path/to/myfile.ext'
              'id': Datafile id, ex. 9a9ea9d7-cebf-401f-814c-343693b177f0
              
          type: str, optional, default='path'
            One of 'path', 'localpath', 'id'
          
          parent: mcapi.Datadir, optional
            Required if requesting Datafiles by 'id'
          
          create: boolean, optional, default False
            If type='path' or 'localpath', and create=True, the Datadir
            will be created if it does not already exist; else raise a ValueError.
          
        Returns
        ----------
          datafile: mcapi.Datafile
            the Datafile with specified key
        
        Notes
        ----------
          May be faster than repeated calls to Project.datafile because fewer
          API calls may be made.
        
        """
        if type == 'id':
            return self._datafiles_by_id(parent, keys)
        elif type == 'localpath':
            return [self._datafile_by_localpath(k, create=create) for k in keys]
        elif type == 'path':
            return [self._child_by_path(k, create=create, type='datafile') for k in keys]
        else:
            raise ValueError("type=" + type + ". type must be one of 'id', 'localpath', 'path'")
    
    
    def _datafiles_by_id(self, parent, ids):
    
        # find which files we don't have yet
        missing = [i for i in ids if i not in self._datafile]
        
        # get any files we don't have
        if len(missing):
            result = api.datafiles_by_id(self.id, missing, remote=self.remote)
            for r in result:
                newfile = Datafile(self, parent, r)
                self._datafile[newfile.id] = newfile
        
        # return list of Datafiles
        return [self._datafile[i] for i in ids]
    
    
    
    
    def _child_by_path(self, path, create=False, type='datafile'):
        """
        Return child by remote path. Ex. 'MyProj/path/to/mydir' or 'MyProj/path/to/myfile.ext'
        
        Arguments
        ----------
          path: str
          
          create: boolean
          
          type: str ('datafile' or 'datadir'), optional, default 'datafile'
            Type to create if not existing
        
        Returns
        ----------
          child: mcapi.Datadir or mcapi.Datafile
            the child found at 'path'. If not existing and create=True, a new 
            object of the specified type will be created in the remote project.
        
        """
        names = string.split(path, '/')
        curr = self.top
        if names[0] != curr.name:
            raise ValueError("Child not found: " + path + ". Could not match: " + names[0])
        for n in names[1:]:
            nextchild = filter(lambda x: x.name == n, curr.children)
            if len(nextchild) == 0:
                if n == names[-1] and create:
                    # still figuring out how this works...
                    if type == 'datadir':
                        data = api.create_datadir(self, path, self.remote)
                        return Datadir(self, curr, data)
                    elif type == 'datafile':
                        data = api.create_datafile(self, path, self.remote)
                        return Datafile(self, curr, data)
                    else:
                      raise ValueError("Unrecognize type: " + type + ". Must be 'datafile' or 'datadir'")
                      
                else:
                    raise ValueError("Child not found: " + path + ". Could not match: " + n)
            curr = nextchild[0]
        return curr
    


def _local_projects():
    """
    Get info on a locally stored Projects.
    
    Returns
    ----------
      projects: List[dict]
        Ex: 
        [{
           'name':'MyProjA', 
           'localpath':'/path/to/MyProjA', 
           'id':'abc123', 
           'lastupload':'0001-01-01 00:00:00+00:00', 
           'lastdownload':'0001-01-01 00:00:00+00:00',
           'remote':'https://materialscommons.org/api'
          },
         ...
        ]
    """
    if not exists(mcdatapath()):
        return dict()
    
    localdbs = glob(join(mcdatapath(), '*.db'))
    localnames = [splitext(basename(f))[0] for f in localdbs]
    
    # currently only one remote at a time
    remote = Remote().mcurl
    
    projects = []
    for name in localnames:
        conn = sqlite3.connect(join(mcdatapath(), name + '.db'))
        cur = conn.cursor()
        
        # get columns
        cur.execute('PRAGMA table_info(project);')
        columns = cur.fetchall()
        
        cur.execute('SELECT * FROM project')
        proj = cur.fetchone()
        
        p = {'remote':remote}
        for col, value in zip(columns, proj):
            if col[1] == 'id':
                # skip SQL id
                continue
            elif col[1] == 'projectid':
                # rename 'projectid' to 'id'
                p['id'] = value
            elif col[1] == 'path':
                # rename 'path' to 'localpath'
                p['localpath'] = value
            else:
                p[col[1]] = value
        projects.append(p)
    
    return projects


def list_projects(remote=mcorg()):
    """
    List Projects.
    
    Arguments
    ----------
      remote: mcapi.Remote, optional, default=mcapi.mcorg()
        where to search for Projects. Default 'remote=mcapi.mcorg()' for the 
        projects stored on materialscommons.org. Use 'remote=None' to return a 
        list of only the projects which are stored locally.
    
    Returns
    ----------
      projects: List[dict]
        A list of project attributes. 
        For all projects:
          'name', 'remote', 'id'
        For locally stored projects only:
          'path', 'lastupload', 'lastdownload'
    """
    if remote is None:
      return _local_projects()
    else:
      results = api.projects(remote)
      projects = []
      locals = _local_projects()
      for r in results:
          name = r['name']
          proj = None
          for p in locals:
              if p['name'] == name and p['remote'] == remote.mcurl:
                  proj = p
                  break
          if proj is None:
              proj = {'name':name, 'remote':remote.mcurl, 'id':r['id']}
          projects.append(proj)
      return projects


def create_project(projname, localpath, remote=mcorg(), upload=False, parallel=3, verbose=True):
    """
    Create remote project from local directory.
    
    Arguments
    ----------
      projname: str
        name of the Project to create. The name of the directory must be the same 
        as the project name.
      
      localpath: str
        location of directory used to create the project. The name of the directory 
        must be the same as the project name.
      
      remote: mcapi.Remote, optional, default mcapi.mcorg()
        where to create the Project. Default uses materialscommons.org.
      
      upload: boolean, optional, default False
        if True, upload files from the new project directory
      
      parallel: integer, optional, default 3
        number of simultaneous uploads to perform
      
      mc: str, optional, default "mc"
        cli program to use 
    
    Returns
    ----------
      (proj, status)
      
      proj: mcapi.Project instance or None
        the Project created, if successful
      
      status: mcapi.CLIResult instance
        Evaluates as True if successful
    """
    if projname != basename(localpath):
        print "projname:", projname
        print "localpath:", localpath, basename(localpath)
        raise Exception("Error creating project: directory name and project name must be the same")
    
    cmd = mccli() + " c p --dir " + localpath + " -n " + str(parallel)
    if upload:
        cmd += " --up"
    cmd += " " + projname
    
    set_cli_remote(remote)
    
    child = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = child.communicate()
    
    status = CLIResult(out, err, child.returncode)
    
    if not status:
      return (None, status)
    else:
      return (Project(localpath=localpath), status)


def clone_project(proj, localpath, remote=mcorg(), download=False, parallel=3, verbose=True):
    """
    Clone remote project to local directory.
    
    Arguments
    ----------
      proj: mcapi.Project instance
        the Project to be cloned. 
      
      localpath: str
        where to clone the project. The name of the directory must be the same as 
        the project name. The directory must already exist. A project can only 
        be cloned to one location locally.
      
      remote: mcapi.Remote, optional, default mcapi.mcorg()
        where to clone the Project from
      
      download: boolean, optional, default False
        if True, upload files from the new project directory
      
      parallel: integer, optional, default 3
        number of simultaneous downloads to perform
      
      mc: str, optional, default "mc"
        cli program to use 
    
    Returns
    ----------
      (proj, status)
      
      proj: mcapi.Project instance
        the Project, updated to include localpath if clone successful
      
      status: mcapi.CLIResult instance
        Evaluates as True if successful
    """
    if proj.name != basename(localpath):
        print "project name:", proj.name
        print "directory name:", basename(localpath)
        raise Exception("Error cloning project: directory name and project name must be the same")
    
    cmd = mccli() + " c p --dir " + localpath + " -n " + str(parallel)
    if download:
        cmd += " --down"
    cmd += " " + basename(localpath)
    
    set_cli_remote(remote)
    
    child = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = child.communicate()
    
    status = CLIResult(out, err, child.returncode)
    
    if not status:
      return (proj, status)
    else:
      return (Project(localpath=localpath), status)


def delete_project(proj):
    """
    Delete database record of project. (Does not delete any files or directories)
    
    Arguments
    ----------
      proj: mcapi.Project instance
        Project to be deleted from local database 
    
    """
    remove(join(mcdatapath(), proj.name+'.db'))

