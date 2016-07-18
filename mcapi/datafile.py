import os
import api, datadir


class Datafile(api.MCObject):
    """
    Materials Commons Datafile provenance object.
    
    Attributes
    ----------
    project: mcapi.Project instance
      the MC Project containing the datafile
    
    parent: mcapi.Datadir instance
      the Datadir containing the datafile
    
    path: str
      the path to the Datafile in the project directory (including the project 
      directory)
      
    size
    uploaded
    checkum
    current
    owner
    
    tags
    notes
    
    mediatype
    
    ToDo: datadirs, processes, samples, atime, usesid, owner, usesid
    
    Note: right now Datafile.id is the 'datafile_id', not 'id' which corresponds to a particular version
    
    """
    
    def __init__(self, project, parent, data=dict()):
        super(Datafile, self).__init__(data)
        
#        print "Constructing Datafile"
#        for k in data.keys():
#          print k, '\t', "'", data[k], "'"
#        print ""
        
        self.project = project
        self.parent = parent
        self.path = os.path.join(parent.path, self.name)
        
        # 'current' version only
        #Note: right now Datafile.id is the 'datafile_id', not 'id' which corresponds to a particular version
        self.id = data.get('datafile_id', None)
        
        attr = ['size', 'uploaded', 'checksum', 'current', 'owner']
        for a in attr:
          setattr(self, a, data.get(a,None)) 
          
        attr = ['tags', 'notes']
        for a in attr:
          setattr(self, a, data.get(a,[])) 
        
        attr = ['mediatype']
        for a in attr:
          setattr(self, a, data.get(a, dict()))
        
        # other attributes:
        #   datadirs, processes, samples, atime, usesid, owner, usesid
        
    @property
    def localpath(self):
        if self.project.localpath is None:
            return None
        else:
            return join(self.project.localpath, relpath(self.path, self.project.name))
    
    
    def upload(self):
        """
        Upload the current local version to Materials Commons. 
        
        Returns
        ----------
          status: mcapi.APIResult instance
            Evaluates as True if successful
        
        Notes
        ----------
        If the file differs from the latest version on Materials Commons a new 
        version is stored.
        """
        return
    
    
    def download(self):
        """
        Download the datafile from Materials Common.
        
        Returns
        ----------
          status: mcapi.APIResult instance
            Evaluates as True if successful
        
        Arguments
        ----------
          force: Boolean, optional, default=True
            If True, overwrite existing file. If False, prompt. 
        
        """
        return
    
    
    def versions(self):
        """
        Returns a list with all versions of this Datafile.
        
        Returns
        ----------
          version_list: List[Datafile]
        
        """
        return

