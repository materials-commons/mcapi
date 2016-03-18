import api


class Sample(object):
    def __init__(self, project_id, name, manufacturer):
        self.project_id = project_id
        self.name = name
        self.description = ''
        self.manufacturer = manufacturer


def create_sample(sample):
    p = Process(sample.project_id, 'as_received', 'As Received', 'As Received')
    p.output_samples.append({'name': sample.name})
    if sample.manufacturer != '':
        p.setup['settings'].append({
            'attribute': 'instrument',
            'name': 'Instrument',
            'properties': [
                {
                    'property': {
                        '_type': 'string',
                        'attribute': 'manufacturer',
                        'name': 'Manufacturer',
                        'description': '',
                        'unit': '',
                        'value': sample.manufacturer
                    }
                }
            ]
        })
    return api.post('projects/' + sample.project_id + '/processes', p.__dict__)

