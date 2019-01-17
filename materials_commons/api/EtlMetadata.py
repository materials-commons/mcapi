from . import api
from .base import MCObject
from .base import _has_key
from .mc_object_utility import make_object


class EtlMetadata(MCObject):
    """
    Materials commons Excel-based ELT metadata.
    Normally created by a call to :func:`materials_commons.api.create_experiment_metadata`
    and retrieved by a call to :func:`materials_commons.api.get_experiment_metadata`
    """

    def __init__(self, data=None):
        self.experiment_id = ''
        self.json = ''

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(EtlMetadata, self).__init__(data)

        attr = ['experiment_id', 'json', 'apikey']
        for a in attr:
            setattr(self, a, data.get(a, None))

    def _process_special_objects(self):
        # undo the effect of general object processing on the json data
        self.json = self.input_data['json']

    def update(self, new_metadata):
        results = api.update_experiment_metadata(self.id, new_metadata, apikey=self.apikey)
        if _has_key('error', results):
            print("Error: ", results['error'])
            return None
        data = results['data']
        data['apikey'] = self.apikey
        updated_metadata_record = make_object(data=data)
        self.json = updated_metadata_record.json
        return self

    def delete(self):
        return api.delete_experiment_metadata(self.id,apikey=self.apikey)
