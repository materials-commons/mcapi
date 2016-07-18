import api, datafile


class Datadir(api.MCObject):
    """
    Materials Commons Datadir
    
    Attributes
    ----------
    project: mcapi.Project
      Project containing this Datadir
    
    localpath: str or None
      absolute path to Datadir on local machine. None if project.localpath is None.
      A directory may not exist locally even if it does exist in the project.
    
    path:
      path to directory from (and including) the top-level directory, 
      ex. 'MyProj/path/to/mydir')
    
    parent: mcapi.Datadir or None
      the Datadir containing this Datadir. If top level Datadir, value is None 
    
    children: List[mcapi.Datadir and mcapi.Datafile] 
      sub-Datadir and Datafiles contained in this Datadir
    
    datadirs: List[mcapi.Datadir] 
      sub-Datadir contained in this Datadir
    
    datafiles: List[mcapi.Datafile]
      Datafiles contained in this Datadir
    
    """
    
    def __init__(self, project, parent, data=dict()):
        
        super(Datadir, self).__init__(data)
        
#        print "Constructing Datadir"
#        for k in data.keys():
#          print k
#        print ""
        
        self.project = project
        self.parent = parent
        
        attr = ['path']
        for a in attr:
          setattr(self, a, data.get(a,None)) 
        
        # ids of all children
        self._children = data.get('children', [])
        
    @property
    def localpath(self):
        if self.project.localpath is None:
            return None
        else:
            return join(self.project.localpath, relpath(self.path, self.project.name))
    
    @property
    def children(self):
        return self.datadirs + self.datafiles
    
    @property
    def datadirs(self):
        ids = [child['id'] for child in self._children if child['_type'] == 'directory'] 
        return self.project.datadirs(ids)
    
    @property
    def datafiles(self):
        ids = [child['id'] for child in self._children if child['_type'] == 'file'] 
        return self.project.datafiles(ids, type='id', parent=self)
    
    def walk(self, topdown=True):
        """
        Analogue to os.walk().
        
        Returns
        ----------
          self, datadirs, datafiles: (mcapi.Datadir, List[mcapi.Datadir], List[mcapi.Datafile])
            Yields 3-tuples of root Datadir, List of sub-Datadir, List of Datafiles
        """
        if topdown:
          yield self, self.datadirs, self.datafiles
        
        for d in self.datadirs:
          for x in d.walk(topdown=topdown):
            yield x
        
        if not topdown:
          yield self, self.datadirs, self.datafiles

                    
