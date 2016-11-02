from mcapi import MCObject, Project, Experiment, Process, Sample, Attribute

def make_object(data):
    holder = make_base_object_for_type(data)
    for key in data.keys():
        value = data['key']
        if (is_object(value)):
            value = make_object(value)
        elif (is_list(value)):
            value = map(make_object,value)
        setattr(holder, key, data.get(key, None))
    return holder

def make_base_object_for_type(data):
    if (data['_type']):
        type = data['_type']
        if (type=='process'):
            return Process(data=data)
        elif (type=='project'):
            return Project(data=data)
        elif (type=='experiment'):
            return Experiment(data=data)
        elif (type=='sample'):
            return Sample(data=data)
        else:
            print "unrecognized type: ", data
            return MCObject(data=data)
    else:
        print "No _type: ", data
        return MCObject(data=data)

def is_object(value):
    return isinstance(value,dict)

def is_list(value):
    return isinstance(value,list)