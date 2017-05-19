from base import MCObject, _data_has_type


class Measurement(MCObject):
    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Measurement, self).__init__(data)
        self.attribute = ''
        self.unit = ''
        self.value = ''
        self.is_best_measure = False
        attr = ['attribute', 'unit', 'value', 'is_best_measure']
        for a in attr:
            setattr(self, a, data.get(a, None))


class MeasurementComposition(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementComposition, self).__init__(data)


class MeasurementString(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementString, self).__init__(data)


class MeasurementMatrix(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementMatrix, self).__init__(data)


class MeasurementVector(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementVector, self).__init__(data)


class MeasurementSelection(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementSelection, self).__init__(data)


class MeasurementFile(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementFile, self).__init__(data)


class MeasurementInteger(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementInteger, self).__init__(data)


class MeasurementNumber(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementNumber, self).__init__(data)


class MeasurementBoolean(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementBoolean, self).__init__(data)


class MeasurementSample(Measurement):
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementSample, self).__init__(data)


def make_measurement_object(obj):
    data = obj
    if isinstance(obj, MCObject):
        data = obj.input_data
    if _data_has_type(data):
        object_type = data['otype']
        holder = None
        if object_type == 'composition':
            holder = MeasurementComposition(data=data)
        if object_type == 'string':
            holder = MeasurementString(data=data)
        if object_type == 'matrix':
            holder = MeasurementMatrix(data=data)
        if object_type == 'vector':
            holder = MeasurementVector(data=data)
        if object_type == 'selection':
            holder = MeasurementSelection(data=data)
        if object_type == 'file':
            holder = MeasurementFile(data=data)
        if object_type == 'integer':
            holder = MeasurementInteger(data=data)
        if object_type == 'number':
            holder = MeasurementNumber(data=data)
        if object_type == 'boolean':
            holder = MeasurementBoolean(data=data)
        if object_type == 'sample':
            holder = MeasurementSample(data=data)
        if object_type == 'file':
            holder = MeasurementFile(data=data)
        if holder:
            holder.process_special_objects()
            return holder
        raise Exception("No Measurement Object, unrecognized otype = " + object_type, data)
    else:
        raise Exception("No Measurement Object, otype not defined", data)