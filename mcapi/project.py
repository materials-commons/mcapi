import api, datadir

class Project(api.MCObject):
    """
    Materials Commons Project object.
    
    Attributes
    ----------
    top: mcapi.Datadir
      Top-level Datadir in this Project
    
    """
    def __init__(self, data=None):
        """
        Arguments
        ----------
        data: dict, optional
          JSON data as obtained from Materials Commons API call
        
        """
        super(Project, self).__init__(data)
        
#        print "Constructing Project"
#        for k in data.keys():
#          print k
#        print ""
        
        self.top = datadir.Datadir(self, api.get('/projects/' + self.id + '/directories'))
        
    
    def walk(self, topdown=True):
        """
        Analogue to os.walk().
        
        Returns
        ----------
          root, datadirs, datafiles: (mcapi.Datadir, List[mcapi.Datadir], List[mcapi.Datafile])
            Yields 3-tuples of root Datadir, List of sub-Datadir, List of Datafiles
        """
        top = self.top
        
        if topdown:
          yield top, top.datadirs, top.datafiles
        
        for d in top.datadirs:
          for x in d.walk(topdown=topdown):
            yield x
        
        if not topdown:
          yield top, top.datadirs, top.datafiles


def get_projects():
    """
    Return a mcapi.Project by id.
    
    Returns
    ----------
      all_proj: List[mcapi.Project]
        A List of all Materials Commons Projects you have access to
    
    """
    return [Project(data=d) for d in api.get('projects')]


def get_project(id):
    """
    Return a mcapi.Project by id.
    
    Returns
    ----------
      proj: mcapi.Project instance
        Materials Commons Project with requested id
    
    Note
    ----------
      Raises ValueError if no Project with requested id
    
    """
    for p in get_projects():
      if p.id == id:
        return p
    raise ValueError("No project with id: " + id)


def get_project_by_name(name):
    """
    Return a mcapi.Project by project name.
    
    Returns
    ----------
      proj: mcapi.Project instance
        Materials Commons Project with requested name
    
    Note
    ----------
      Raises ValueError if no Project with requested name
    
    """
    for p in get_projects():
      if p.name == name:
        return p
    raise ValueError("No project named: " + name)
