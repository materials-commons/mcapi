import api
from api import MCObject


#class Sample(MCObject):
#    def __init__(self, project_id, name, manufacturer):
#        self.project_id = project_id
#        self.name = name
#        self.description = ''
#        self.manufacturer = manufacturer
#
#
#def create_sample(sample):
#    p = Process(sample.project_id, 'as_received', 'As Received', 'As Received')
#    p.output_samples.append({'name': sample.name})
#    if sample.manufacturer != '':
#        p.setup['settings'].append({
#            'attribute': 'instrument',
#            'name': 'Instrument',
#            'properties': [
#                {
#                    'property': {
#                        '_type': 'string',
#                        'attribute': 'manufacturer',
#                        'name': 'Manufacturer',
#                        'description': '',
#                        'unit': '',
#                        'value': sample.manufacturer
#                    }
#                }
#            ]
#        })
#    return api.post('projects/' + sample.project_id + '/processes', p.__dict__)


class Sample(MCObject):
    """
    Materials Commons Sample provenance object.
    
    Attributes
    ----------
    project: mcapi.Project instance  (? should be list of...)
      the MC Project containing the sample
    
    path: str
      the relative path to the Datafile in the project directory
    
    """
    
    def __init__(self):
        super(MCObject, self).__init__()
        self.project = None
        self.path = None
        
    
    def create(self):
        """
        Create this as new Sample object on Materials Commons. 
        
        Returns
        ----------
          status: boolean
            Returns True if successfully created
        
        """
        return False
    
    
    def versions(self):
        """
        Returns a list with all versions of this Sample.
        
        Returns
        ----------
          version_list: (List[Sample])
        
        """
        return []


def get_sample(project, id):
    """
    Get Sample object from Materials Commons by id. 
    
    Arguments
    ----------
      project: mcapi.Project instance
        the MC Project containing the Datafile
      
      id: str
        the Sample id
      
      
    Returns
    ----------
      sample: mcapi.Sample instance
    
    """
    return


def get_sample_by_name(project, name):
    """
    Get Sample object from Materials Commons by name. 
    
    Arguments
    ----------
      project: mcapi.Project instance
        the MC Project containing the Sample
      
      name: str
        the name of the Sample
      
      
    Returns
    ----------
      sample: mcapi.Sample instance
    
    """
    return 