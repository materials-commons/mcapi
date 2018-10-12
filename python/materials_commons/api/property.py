from __future__ import unicode_literals

import sys
from io import StringIO
import re
import datetime

from .base import MCObject, PrettyPrint
from .measurement import make_measurement_object


class Property(MCObject):
    """
    A Materials Commons Property.
    Normally created by calls to :func:`mcapi.Process.set_measurements_for_process_samples`
    or :func:`mcapi.Process.update_setup_properties`.
    """

    def __init__(self, data=None):
        self.id = ''  #: this property's id
        self.name = ''  #:
        self.description = ''  #:
        self.setup_id = ''  #: the id of the setup, if set indicates that this is a setup property
        self.property_set_id = ''  #: the property_set id, if set this property for measurement
        self.parent_id = ''  #: previous version of this property, if any
        self.property_id = ''  #: this property's id
        self.required = False  #: a required property?
        self.unit = ''  #: unit, if any
        self.attribute = ''  #: attribute
        self._value = ''  #: value - is actually set and fetched by covering methods on 'value'

        self.best_measure_id = None  #: used when Property is in a Measurement

        self.units = []  #: array of string
        self.choices = []  #: array of string

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Property, self).__init__(data)

        attr = ['setup_id', 'required', 'unit', 'attribute', 'value']
        for a in attr:
            setattr(self, a, data.get(a, None))

        attr = ['units', 'choices']
        for a in attr:
            setattr(self, a, data.get(a, []))

    @property
    def value(self):
        return self._get_value()

    @value.setter
    def value(self, value):
        self._set_value(value)

    # to provide selective overriding in subclass
    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = value

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
        pp.write("id: " + pp.str(self.id))
        if hasattr(self, 'best_measure') and self.best_measure is not None:
            pp.write("best_measure_id: " + pp.str(self.best_measure_id))
            pp.write_pretty_print_objects("best_measure: ", self.best_measure)
        strout = StringIO()
        strout.write(self.value)
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

    def verify_value_type(self, value):
        """

        :param value:
        :return: None
        :raises: MCPropertyException when value does not match type

        """

        # TODO: set verify for all types
        # raise MCPropertyException('Attempt to verify value type for generic Property - use appropriate subclass')
        pass


class MeasuredProperty(Property):
    """
    A property that is associated with a measurement.

    See :class:`mcapi.Property`

    """

    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner',
        # 'setup_id', 'required', 'unit', 'attribute', 'value', 'units', 'choices']
        super(MeasuredProperty, self).__init__(data)

        self.best_measure = []  # of Measurement
        self.best_measure_id = ''

        attr = ['best_measure_id']
        for a in attr:
            setattr(self, a, data.get(a, ''))

        attr = ['best_measure']
        for a in attr:
            setattr(self, a, data.get(a, []))

    def _process_special_objects(self):
        if self.best_measure:
            for i in range(len(self.best_measure)):
                measure_data = self.best_measure[i]
                measurement = make_measurement_object(measure_data)
                self.best_measure[i] = measurement


class NumberProperty(Property):
    """
    See :class:`mcapi.Property`
    """

    def __init__(self, data=None):
        super(NumberProperty, self).__init__(data)


class StringProperty(Property):
    """
    See :class:`mcapi.Property`
    """

    def __init__(self, data=None):
        super(StringProperty, self).__init__(data)


class BooleanProperty(Property):
    """
    See :class:`mcapi.Property`
    """

    def __init__(self, data=None):
        super(BooleanProperty, self).__init__(data)


class DateProperty(Property):
    """
    See :class:`mcapi.Property`
    """

    def __init__(self, data=None):
        super(DateProperty, self).__init__(data)


class SelectionProperty(Property):
    """
    See :class:`mcapi.Property`
    """

    def __init__(self, data=None):
        super(SelectionProperty, self).__init__(data)

    def verify_value_type(self, value):
        if isinstance(value, dict):
            if isinstance(value['name'], str) and isinstance(value['value'], str):
                return
        if not isinstance(value, str):
            message = "Only str/unicode values for a SelectionProperty; "
            message += "value = '" + str(value) + "', type = " + str(type(value)) + " is not valid"
            raise MCPropertyException(message)
        for choice in self.choices:
            if "Other" == choice['name']:
                return
        found = False
        for choice in self.choices:
            if value == choice['name'] or value == choice['value']:
                found = True
        if not found:
            values = []
            names = []
            for choice in self.choices:
                values.append(choice['value'])
                names.append(choice['name'])
            message = "Choice '" + value + "' is not valid for this property; "
            message += "valid choices are " + ", ".join(names) + ", " + ", ".join(values)
            raise MCPropertyException(message)

    def _set_value(self, value):
        # note: assumes that verify_value_type has been called
        if not value:
            self._value = value
            return
        # note: if choices is empty, we are in init stage
        if len(self.choices) == 0:
            self._value = value
            return
        # this is non-init stage with a non-None value
        found = None
        has_other = False
        for choice in self.choices:
            if choice['value'] == 'other':
                has_other = True
            if value == choice['name'] or value == choice['value']:
                found = choice
                break
        if has_other and not found:
            found = {"name": "Other", "value": value}
        self._value = found


class MCPropertyException(BaseException):
    pass


class FunctionProperty(Property):
    """
    See :class:`mcapi.Property`
    """

    def __init__(self, data=None):
        super(FunctionProperty, self).__init__(data)


class CompositionProperty(Property):
    """
    See :class:`mcapi.Property`
    """

    def __init__(self, data=None):
        super(CompositionProperty, self).__init__(data)


class VectorProperty(Property):
    """
    See :class:`mcapi.Property`
    """

    def __init__(self, data=None):
        super(VectorProperty, self).__init__(data)


class MatrixProperty(Property):
    """
    See :class:`mcapi.Property`
    """

    def __init__(self, data=None):
        super(MatrixProperty, self).__init__(data)


# ---------------- Note these property-related utility functions are used ---------------------
# ---------------- in other files (look for 'from .property import')      ---------------------

re1 = re.compile(r"\s+")
re2 = re.compile(r"/+")


def _normalise_property_name(name):
    if name:
        name = name.replace('-', '_')
        name = re1.sub("_", name)
        name = re2.sub("_", name)
        name = name.lower()
    return name


def _convert_for_json_if_datetime(value):
    if isinstance(value, datetime.date):
        return value.ctime()
    else:
        return None
