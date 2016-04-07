import api, datafile


class Datadir(api.MCObject):
    """
    Materials Commons Datadir
    
    Attributes
    ----------
    project: mcapi.Project
      Project containing this Datadir
    
    children: List[mcapi.Datadir and mcapi.Datafile] 
      sub-Datadir and Datafiles contained in this Datadir
    
    datadirs: List[mcapi.Datadir] 
      sub-Datadir contained in this Datadir
    
    datafiles: List[mcapi.Datafile]
      Datafiles contained in this Datadir
    
    """
    
    def __init__(self, project, data=dict()):
        super(Datadir, self).__init__(data)
        
#        print "Constructing Datadir"
#        for k in data.keys():
#          print k
#        print ""
        
        self.project = project
        
        attr = ['path']
        for a in attr:
          setattr(self, a, data.get(a,None)) 
        
        self._children = data.get('children', [])
        self._datadirs = None
        self._datafiles = None
    
    @property
    def children(self):
        return self.datadirs + self.datafiles
    
    @property
    def datadirs(self):
        if self._datadirs is None:
            self._datadirs = []
            for child in self._children:
                if child['_type'] == 'directory':
                    self._datadirs.append(get_datadir(self.project, child['id']))
        return self._datadirs
    
    @property
    def datafiles(self):
        if self._datafiles is None:
            self._datafiles = []
            for child in self._children:
                if child['_type'] == 'file':
                    self._datafiles.append(datafile.get_datafile(self.project, self, child['id']))
        return self._datafiles
    
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


def get_datadir(project, id):
    result = api.get('/projects/' + project.id + '/directories/' + id)
    return Datadir(project, result)


                    
