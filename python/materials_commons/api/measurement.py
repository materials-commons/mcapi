from .base import MCObject, PrettyPrint, _data_has_type
import sys
from io import StringIO


class Measurement(MCObject):
    """
    A Materials Commons measurement.

    Normally set by :func:`mcapi.Process.set_measurements_for_process_samples`.
    """
    def __init__(self, data=None):
        self.id = ''                        #: this measurement's id
        self.name = ''                      #:
        self.description = ''               #:
        self.attribute = ''                 #:
        self.unit = ''                      #:
        self.value = ''                     #:
        self.file = None                    #:
        self.is_best_measure = False        #:
        self.measurement_id = ''            #:
        self.sample_id = ''                 #:
        self.property_id = ''               #:

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Measurement, self).__init__(data)

        attr = ['attribute', 'unit', 'value', 'is_best_measure',
                'measurement_id', 'sample_id', 'property_id', 'file']
        for a in attr:
            setattr(self, a, data.get(a, None))

    def abbrev_print(self, shift=0, indent=2, out=sys.stdout):
        self.pretty_print(shift=shift, indent=indent, out=out)

    def pretty_print(self, shift=0, indent=2, out=sys.stdout):
        """
        Prints a nice layout of the object and all of it's values.

        :param shift: the offset from the start of the line, in increments of indent
        :param indent: the indent used for layout, in characters
        :param out: the stream to which the object in printed
        :return: None
        """
        pp = PrettyPrint(shift=shift, indent=indent, out=out)
        pp.write("attribute: " + pp.str(self.attribute))
        pp.n_indent += 1
        # Note: Measurement in Process, outside of actual measurement, has no id
        if self.id:
            pp.write("id: " + pp.str(self.id))
            pp.write("measurement_id: " + pp.str(self.measurement_id))
            pp.write("property_id: " + pp.str(self.property_id))
            pp.write("sample_id: " + pp.str(self.sample_id))
        strout = StringIO()
        strout.write(str(self.value))
        lines = strout.getvalue().splitlines()
        if self.value is None:
            pp.write("value: " + pp.str(self.value))
        else:
            if hasattr(self, 'unit'):
                pp.write("unit: " + pp.str(self.unit))
            elif hasattr(self, 'units'):
                pp.write("units: " + pp.str(self.units))
            if len(lines) == 1:
                pp.write("value: " + pp.str(self.value))
            else:
                pp.write("value: ")
                pp.n_indent += 1
                for line in lines:
                    pp.write(line)
                pp.n_indent -= 1


class MeasurementComposition(Measurement):
    """
    See :class:`mcapi.Measurement`
    """
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementComposition, self).__init__(data)


class MeasurementString(Measurement):
    """
    See :class:`mcapi.Measurement`
    """
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementString, self).__init__(data)


class MeasurementMatrix(Measurement):
    """
    See :class:`mcapi.Measurement`
    """
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementMatrix, self).__init__(data)


class MeasurementVector(Measurement):
    """
    See :class:`mcapi.Measurement`
    """
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementVector, self).__init__(data)


class MeasurementSelection(Measurement):
    """
    See :class:`mcapi.Measurement`
    """
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementSelection, self).__init__(data)


class MeasurementFile(Measurement):
    """
    See :class:`mcapi.Measurement`
    """
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementFile, self).__init__(data)


class MeasurementInteger(Measurement):
    """
    See :class:`mcapi.Measurement`
    """
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementInteger, self).__init__(data)


class MeasurementNumber(Measurement):
    """
    See :class:`mcapi.Measurement`
    """
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementNumber, self).__init__(data)


class MeasurementBoolean(Measurement):
    """
    See :class:`mcapi.Measurement`
    """
    def __init__(self, data=None):
        # attr = ['name', 'attribute', 'birthtime', 'mtime', 'otype', 'owner', 'unit', 'value']
        super(MeasurementBoolean, self).__init__(data)


class MeasurementSample(Measurement):
    """
    See :class:`mcapi.Measurement`
    """
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
            holder._process_special_objects()
            return holder
        raise Exception("No Measurement Object, unrecognized otype = " + object_type, data)
    else:
        raise Exception("No Measurement Object, otype not defined", data)
