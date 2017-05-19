import datetime


class MCObject(object):
    def __init__(self, data=None):
        self.otype = "unknown"
        self.owner = ""
        self.name = ""
        self.description = ""
        self.id = ""
        self.birthtime = None
        self.mtime = None
        if not data:
            data = {}

        self.input_data = data
        self.shallow = True

        attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        for a in attr:
            setattr(self, a, data.get(a, None))

    def process_special_objects(self):
        data = self.input_data
        if not data:
            return
        if _has_key('otype', data):
            obj_type = data['otype']
            # these types are properties and measurements and they get out of jail free
            pass_types = ['number', 'string', 'boolean', 'date', 'selection', 'function',
                          'composition', 'vector', 'matrix']
            if obj_type in pass_types:
                return

            # these cases may need to be further investigated ???
            #  - some of these are sub-classes - to be revisited
            unexpected_types = ['property', 'sample', 'experiment_task', 'experiment', 'settings']
            if obj_type in unexpected_types:
                return
        if _has_key('value', data) and _has_key('element', data):
            return
        if _has_key('value', data) and _has_key('name', data):
            return
        if _has_key('value', data) and _has_key('unit', data):
            return
        if _has_key('attribute', data) and data['attribute'] == 'instrument':
            return
        if _has_key('starred', data):
            return
        if _has_key('mime', data):
            return
        if _has_key('property_set_id', data) and _has_key('name', data):
            return


# -- general support functions
def _decorate_object_with(obj, attr_name, attr_value):
    setattr(obj, attr_name, attr_value)
    return obj


def _is_object(value):
    return isinstance(value, dict)


def _is_list(value):
    return isinstance(value, list)


def _has_key(key, data):
    return _is_object(data) and key in data.keys()


def _data_has_type(data):
    return _has_key('otype', data)


def _is_datetime(data):
    return _has_key('$reql_type$', data) and data['$reql_type$'] == 'TIME'


def _make_datetime(data):
    timestamp = int(data['epoch_time'])
    return datetime.datetime.utcfromtimestamp(timestamp)
