from mcapi import MCObject, api

class Sample(MCObject):
    def __init__(self,name=None, data=None):
        self.pproperty_set_id = ''

        if (not data): data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        super(Sample, self).__init__(data)

        attr = ['property_set_id']
        for a in attr:
            setattr(self, a, data.get(a, None))

def create_samples(project_id, process_id, sample_names):
    samples_array_dict = api.create_samples(project_id, process_id, sample_names)
    samples_array = samples_array_dict['samples']
    return map((lambda x: Sample(data=x)), samples_array)

__samples_example__ = {u'samples': [
    {u'property_set_id': u'702de353-739a-445f-b687-8479bb73a492', u'name': u'Test Sample 1',
     u'id': u'4d3d997e-22c5-4036-9365-64cf910f715e'}]}
