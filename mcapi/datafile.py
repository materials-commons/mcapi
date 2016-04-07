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
        
        
    
    def create(self):
        """
        Create this as new Datafile object on Materials Commons. 
        
        
        Note
        ----------
        Upload file separately using Datafile.upload.
        """
        return
    
    
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


def get_datafile(project, parent, id):
    """
    Get Datafile object from Materials Commons by path. 
    
    Arguments
    ----------
      project: mcapi.Project instance
        the MC Project containing the Datafile
      
      parent: mcapi.Datadir instance
        the Datadir containing the Datafile
      
      id: str
        the Datafile id
      
    Returns
    ----------
      datafile: mcapi.Datafile instance
    
    Note
    ----------
      Download file separately using Datafile.download.
    """
    return Datafile(project, parent, data=api.get('projects/' + project.id + '/files/' + id))


def get_datafile_by_name(project, parent, name):
    """
    Get Datafile object from Materials Commons by path. (latest version)
    
    Arguments
    ----------
      project: mcapi.Project instance
        the MC Project containing the Datafile
      
      parent: mcapi.Datadir instance
        the Datadir containing the Datafile
      
      name: str
        the name of the Datafile 
      
    Returns
    ----------
      datafile: mcapi.Datafile instance
    
    Note
    ----------
      Download file separately using Datafile.download.
    """
    basepath = 'projects/' + project.id + '/files_by_path'
    params = {'file_path': parent.path + '/' + name}
    return Datafile(project, parent, data=api.put(basepath, params=params))

