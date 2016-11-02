from mcapi import MCObject, Project, Experiment, Process, Sample
from datetime import utcfromtimestamp

def make_object(data):
    holder = make_base_object_for_type(data)
    for key in data.keys():
        value = data[key]
        if (is_object(value)):
            value = make_object(value)
        elif (is_list(value)):
            value = map(make_object,value)
        setattr(holder, key, value)
    return holder

def make_base_object_for_type(data):
    if (data_has_type(data)):
        type = data['_type']
        if (type=='process'):
            return Process(data=data)
        if (type=='project'):
            return Project(data=data)
        if (type=='experiment'):
            return Experiment(data=data)
        if (type=='sample'):
            return Sample(data=data)
        if (type=='experiment_task'):
            # print ("Experiment task not implemented")
            return MCObject(data=data)
        else:
            # print "unrecognized type: ", data
            return MCObject(data=data)
    else:
        if (has_key('timezone',data)):
            return utcfromtimestamp(data['time'])
            return MCObject(data=data)
        if (has_key('unit',data)):
            # print ("Unit not implemented")
            return MCObject(data=data)
        if (has_key('starred',data)):
            # print ("Flags not implemented")
            return MCObject(data=data)
        # print "No _type: ", data
        return MCObject(data=data)

def is_object(value):
    return isinstance(value,dict)

def is_list(value):
    return isinstance(value,list)

def has_key(key,data):
    return key in data.keys()

def data_has_type(data):
    return has_key('_type',data)
