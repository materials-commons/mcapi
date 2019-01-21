import sys

from . import api
from .base import MCObject, PrettyPrint
from .make_objects import make_object, make_measured_property


class Sample(MCObject):
    """
    A Materials Commons Sample.

    .. note:: Normally created from the database by a call to :func:`mcapi.Process.create_samples`
        using a 'create sample' style process.

    """

    def __init__(self, name=None, data=None):
        self.id = None  #: id for this Sample - string
        self.name = ""  #: name for this Sample - string

        self.property_set_id = ''  #: the id of the related property set
        self.project = None  #: the project that 'contains' this Sample
        self.experiment = None  #: the experiment that 'contains' this Sample
        # filled in when measurements exist (?)
        self.properties = []  #: when measurements exist - the properties of this sample
        self.experiments = []  #: the experiments that create or transform this sample
        self.property_set_id = None  #: the id of the property_set for this sample
        self.direction = ''  #: the direction relationship ('input' or 'output') that sample
        self.sample_id = None
        # to be filled in later
        self.processes = {}
        self.files = []
        self.is_grouped = False
        self.has_group = False
        self.group_size = 0

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Sample, self).__init__(data)

        attr = ['property_set_id', 'direction', 'sample_id',
                'process_id', 'is_grouped', 'has_group', 'group_size']
        for a in attr:
            setattr(self, a, data.get(a, None))

        attr = ['properties', 'files', 'experiments']
        for a in attr:
            setattr(self, a, data.get(a, []))

        if name:
            self.name = name

    def pretty_print(self, shift=0, indent=2, out=sys.stdout):
        """
        Prints a nice layout of the object and all of it's values.

        :param shift: the offset from the start of the line, in increments of indent
        :param indent: the indent used for layout, in characters
        :param out: the stream to which the object in printed
        :return: None
        """
        pp = PrettyPrint(shift=shift, indent=indent, out=out)
        pp.write("name: " + pp.str(self.name))
        pp.n_indent += 1
        pp.write("description: " + pp.str(self.description))
        pp.write("id: " + pp.str(self.id))
        pp.write("owner: " + pp.str(self.owner))
        if len(self.files) > 0:
            pp.write_objects("files: ", self.files)
        if len(self.experiments) > 0:
            pp.write_objects("experiments: ", self.experiments)
        if self.direction:
            pp.write("direction: " + pp.str(self.direction))
            pp.write("property_set_id: " + pp.str(self.property_set_id))
            pp.write("sample_id: " + pp.str(self.sample_id))
            pp.write_objects("experiments: ", self.experiments)
            pp.write_pretty_print_objects("properties: ", self.properties)
        if len(self.processes) == 0:
            self.decorate_with_processes()
        pp.write("processes: ")
        pp.n_indent += 1
        for p in self.processes:
            pp.write(pp.str(p.name))
            pp.n_indent += 1
            pp.write("id: " + pp.str(p.id))
            pp.write_measurements(p.measurements)
            pp.n_indent -= 1

    def _process_special_objects(self):
        if self.properties:
            self.properties = [make_measured_property(p.input_data) for p in self.properties]

    # Sample - basic methods: rename, put, delete
    def rename(self):  # , name):
        """
        Rename sample.

        :return: this

        .. note:: Currently not implemented

        """
        # TODO: Sample.rename(name)
        raise NotImplementedError("Sample.rename(name) is not implemented")
        pass

    def put(self):
        """
        Copy local values to database.

        :return: this

        .. note:: Currently not implemented

        """
        # TODO: Sample.put()
        raise NotImplementedError("Sample.put() is not implemented")
        pass

    def delete(self):
        """
        Delete a sample. The sample is removed from the database leaving only the
        local copy. A sample can not be deleted if any of the following are true:
        ... ? ...

        :return: id - the id of the sample deleted or None (if the sample was not deleted)

        """
        property_set_id = None
        proc_id = None
        for proc in self.input_data['processes']:
            if proc['category'] == 'create_sample' and proc['direction'] == 'out':
                property_set_id = proc['property_set_id']
                proc_id = proc['id']
                break
        if proc_id is None:
            results = None
        else:
            results = api.delete_sample_created_by_process(
                self.project.id, proc_id, self.id, property_set_id, apikey=self.project._apikey)

        return results

    # Sample - additional methods
    def link_files(self, file_list):
        """
        Link files to sample

        :param file_list: list of :class:`mcapi.mc.File` instances
        :return: instance of :class:`mcapi.mc.Sample` - the updated sample
        """
        id_list = []
        for file in file_list:
            id_list.append(file.id)
        api.link_files_to_sample(self.project.id, self.id, id_list, apikey=self.project._apikey)
        return self.update_with_details()

    def update_with_details(self):
        updated_sample = self.project.fetch_sample_by_id(self.id)
        updated_sample.project = self.project
        updated_sample.experiment = self.experiment
        return updated_sample

    def decorate_with_processes(self):
        filled_in_sample = make_object(api.fetch_sample_details(self.project.id, self.id, apikey=self.project._apikey))
        self.processes = filled_in_sample.processes
        return self
