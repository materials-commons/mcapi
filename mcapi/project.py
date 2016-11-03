import api
from mcobject import MCObject

class Project(MCObject):
    """
    Materials Commons Project object.
    
    Attributes
    ----------
    (those of MCObject, plus...)

    top: mcapi.Datadir
      Top-level Datadir in this Project
    
    source: a URL string or None
      Where this project is hosted
    
    """
    
    def __init__(self, name=None, description=None, id=None, remote_url=None, data=dict()):
        """
        Arguments
        ----------
        name: str, optional
        descrition: str, optional
        id: str, optional
            project id
        remote_url: rul, str
            host of the project, optional
        data:
            generally, data in dictionary form, as returned from the rest api
        """
        self.source = remote_url

        if (name):
            data['name'] = name

        if (description):
            data['description'] = description

        if (id):
            data['id'] = id

        super(Project, self).__init__(data)

#        print "Constructing Project"
#        for k in data.keys():
#          print k
#        print ""
        
        self._top = None
        
        # holds Datadir, using id for key; initally empty, additional calls needed to fill
        self._datadir = dict()
        
        # holds Datafile, using id for key;  initally empty, additional calls needed to fill
        self._datafile = dict()


def list_projects():
    results = api.projects()
    projects = []
    for r in results:
        projects.append(Project(r))
    return projects

def create_project(name,description):
    ids = api.create_project(name,description)
    project_id = ids['project_id']
    project = Project(name=name, description=description, id=project_id,data=ids)
    return project
