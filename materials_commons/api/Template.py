import sys
from io import StringIO
from pandas import DataFrame
from tabulate import tabulate

from .base import MCObject, PrettyPrint


class Template(MCObject):
    """
    A Materials Commons Template.

    .. note:: Only available through the top level function get_all_templates().

    .. note:: Template is truncated as we only need
        the id to create processes from a Template, and this is
        the only way in which Template is used, for now.

    """
    # global static
    create = "global_Create Samples"  #: a typical template id, used for testing.
    compute = "global_Computation"
    primitive_crystal_structure = "global_Primitive Crystal Structure"

    def __init__(self, data=None):
        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Template, self).__init__(data)

        # ---- NOTE
        # - Template is truncated as we only need the id to create
        # - processes from a Template
        # ----

    def pretty_print(self, shift=0, indent=2, out=sys.stdout):
        """
        Prints a nice layout of the object and all of it's values.

        :param shift: the offset from the start of the line, in increments of indent
        :param indent: the indent used for layout, in characters
        :param out: the stream to which the object in printed
        :return: None
        """
        pp = PrettyPrint(shift=shift, indent=indent, out=out)
        _data = self.input_data
        pp.write("name: " + pp.str(self.name))
        pp.n_indent += 1
        value_list = ['description', 'id', 'category', 'process_type', 'destructive', 'does_transform']
        for k in value_list:
            pp.write(k + ": " + pp.str(_data[k]))

        # for 'create sample' processes
        measurements = _data['measurements']
        if len(measurements):
            pp.write("")
            pp.write("Create samples with attributes:\n")
            df = DataFrame.from_records(measurements, columns=['name', 'attribute', 'otype', 'units'])
            strout = StringIO()
            strout.write(tabulate(df, showindex=False, headers=['name', 'attribute', 'otype', 'units']))
            for line in strout.getvalue().splitlines():
                pp.write(line)

        # for process settings / attributes
        setup = _data['setup']

        # attributes are grouped, for each group print()attributes
        for s in setup:
            properties = s['properties']
            if len(properties):
                pp.write("")
                pp.write("Process attributes: " + s['name'] + "\n")
                df = DataFrame.from_records(properties, columns=['name', 'attribute', 'otype', 'units'])
                strout = StringIO()
                strout.write(tabulate(df, showindex=False, headers=['name', 'attribute', 'otype', 'units']))
                for line in strout.getvalue().splitlines():
                    pp.write(line)
