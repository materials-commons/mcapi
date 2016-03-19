import api
from api import MCObject


class Datafile(MCObject):
    """
    Materials Commons Datafile provenance object.
    
    Attributes
    ----------
    project: mcapi.Project instance
      the MC Project containing the datafile
    
    path: str
      the relative path to the Datafile in the project directory
    
    version_id: str
      id of the version of the Datafile
    
    """
    
    def __init__(self):
        super(MCObject, self).__init__()
        self.project = None
        self.path = None
        self.version_id = None
    
    
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
        
        Notes
        ----------
        If the file differs from the latest version on Materials Commons a new 
        version is stored.
        """
        return
    
    
    def download(self, force=False):
        """
        Download the datafile from Materials Common.
        
        Arguments
        ----------
          force: Boolean, optional, default=True
            If True, overwrite existing file. If False, prompt. 
        
        """
        return
    
    
    def versions(self):
        """
        Returns a list with all other versions of this Datafile.
        
        Returns
        ----------
          version_list: (List[Datafile])
        
        """
        return


def get_datafile(project, datafile_id, version_id=None):
    """
    Get Datafile object from Materials Commons by path. 
    
    Arguments
    ----------
      project: mcapi.Project instance
        the MC Project containing the Datafile
      
      datafile_id: str
        the Datafile id
      
      version_id: str
        the version of the Datafile requested. Default returns latest version.
    
    Returns
    ----------
      datafile: mcapi.Datafile instance
    
    Note
    ----------
      Download file separately using Datafile.download.
    """
    return


def get_datafile_by_path(project, path, version_id=None):
    """
    Get Datafile object from Materials Commons by path. 
    
    Arguments
    ----------
      project: mcapi.Project instance
        the MC Project containing the Datafile
      
      path: str
        the relative path to the Datafile in the project directory
      
      version_id: str
        the version of the Datafile requested. Default returns latest version.
    
    Returns
    ----------
      datafile: mcapi.Datafile instance
    
    Note
    ----------
      Download file separately using Datafile.download.
    """
    return 

