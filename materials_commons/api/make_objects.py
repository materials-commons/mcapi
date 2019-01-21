import copy
import json

from .base import MCObject, _has_key, _data_has_type
from .base import _is_object, _is_list
from .base import _is_datetime, _make_datetime


def make_object(data):
    try:
        if _is_datetime(data):
            return _make_datetime(data)
        if _is_object(data):
            holder = make_base_object_for_type(data)
            for key in data.keys():
                value = copy.deepcopy(data[key])
                if _is_object(value):
                    value = make_object(value)
                elif _is_list(value):
                    value = [make_object(x) for x in value]
                setattr(holder, key, value)
            holder._process_special_objects()
            return holder
        else:
            return data
    except Exception as e:
        msg = "---\nData:\n" + json.dumps(data, indent=2) + "\n" \
              + "---\nFailed:" + str(e) + "\n" \
              + "---\n"
        raise Exception("Failed to make object: \n" + msg)


def make_base_object_for_type(data):
    from .Project import Project
    from .File import File
    from .User import User
    from .Template import Template
    from .Directory import Directory
    from .Experiment import Experiment
    from .Process import Process
    from .EtlMetadata import EtlMetadata
    from .Sample import Sample

    if _has_key('_type', data):  # catch, convert legacy objects
        data['otype'] = data['_type']
    if _data_has_type(data):
        object_type = data['otype']
        if object_type == 'process':
            return Process(data=data)
        if object_type == 'project':
            return Project(data=data)
        if object_type == 'experiment':
            return Experiment(data=data)
        if object_type == 'sample':
            return Sample(data=data)
        if object_type == 'datadir':
            return Directory(data=data)
        if object_type == 'directory':
            return Directory(data=data)
        if object_type == 'datafile':
            return File(data=data)
        if object_type == 'file':
            return File(data=data)
        if object_type == 'template':
            return Template(data=data)
        if object_type == 'experiment_etl_metadata':
            return EtlMetadata(data=data)
        if object_type == 'experiment_task':
            # Experiment task not implemented
            return MCObject(data=data)
        else:
            return MCObject(data=data)
    else:
        if _has_key('fullname', data):
            return User(data=data)
        if _has_key('unit', data):
            return MCObject(data=data)
        if _has_key('starred', data):
            return MCObject(data=data)
        return MCObject(data=data)


def make_property_object(obj):
    from .property import Property, NumberProperty, StringProperty, BooleanProperty, VectorProperty
    from .property import DateProperty, SelectionProperty, FunctionProperty, MatrixProperty
    from .property import CompositionProperty
    data = obj
    if isinstance(obj, MCObject):
        data = obj.input_data
    if _has_key('_type', data):  # catch, convert legacy objects
        data['otype'] = data['_type']
    if _data_has_type(data):
        object_type = data['otype']
        holder = None
        if object_type == 'number':
            holder = NumberProperty(data=data)
        if object_type == 'string':
            holder = StringProperty(data=data)
        if object_type == 'boolean':
            holder = BooleanProperty(data=data)
        if object_type == 'date':
            holder = DateProperty(data=data)
        if object_type == 'selection':
            holder = SelectionProperty(data=data)
        if object_type == 'function':
            holder = FunctionProperty(data=data)
        if object_type == 'composition':
            holder = CompositionProperty(data=data)
        if object_type == 'vector':
            holder = VectorProperty(data=data)
        if object_type == 'matrix':
            holder = MatrixProperty(data=data)
        if not holder:
            # raise Exception("No Property Object, unrecognized otype = " + object_type, data)
            holder = Property(data=data)
        holder._process_special_objects()
        return holder
    else:
        raise Exception("No Property Object, otype not defined", data)


def make_measured_property(data):
    from .property import MeasuredProperty
    measurement_property = MeasuredProperty(data)
    measurement_property._process_special_objects()
    return measurement_property
