import sys

from io import StringIO
from os import listdir
from os import path as os_path
from pandas import DataFrame
from tabulate import tabulate

from . import api
from .base import MCObject, PrettyPrint
from .base import _decorate_object_with, _has_key
from .make_objects import make_object, make_property_object, make_measured_property
from .measurement import make_measurement_object
from .property_util import _normalise_property_name, _convert_for_json_if_datetime


# -- top level user function ---
def get_all_users():
    """
    Return the list of all users registered on the server.

    :return: a list of :class:`mcapi.User`

    >>> user_list = get_all_users()
    >>> for user in user_list:
    >>>     print(user.fullname, user.email)

    """
    results = api.get_all_users()
    users = [make_object(u) for u in results['val']]
    return users


# -- top level template function ---
def get_all_templates():
    """
    Return a list of all the templates known to the system.

    :return: a list of :class:`mcapi.Template`

    >>> template_list = get_all_templates()
    >>> for template in template_list:
    >>>     print(template.name, template.id)

    """
    templates_array = api.get_all_templates()
    templates = [make_object(t) for t in templates_array]
    return templates


# -- top level functions for experiment etl metadata
def create_experiment_metadata(experiment_id, metadata):
    """
    Create a metadata record for Excel-based experiment workflow ETL.

    :param experiment_id: the id of an existing experiment
    :param metadata: the metadata for the experiment; see :class:`materials_commons.etl.input.build_project.BuildProjectExperiment`
    :return: a object of :class:`materials_commons.api.EtlMetadata`
    """
    results = api.create_experiment_metadata(experiment_id, metadata)
    if _has_key('error', results):
        print("Error: ", results['error'])
        return None
    data = results['data']
    return make_object(data=data)


def get_experiment_metadata_by_experiment_id(experiment_id):
    """
    Fetch an existing metadata record for Excel-based experiment workflow ETL.

    :param experiment_id: the id of an existing experiment
    :return: a object of :class:`materials_commons.api.EtlMetadata`
    """
    results = api.get_experiment_metadata_by_experiment_id(experiment_id)
    if _has_key('error', results):
        print("Error: ", results['error'])
        return None
    data = results['data']
    return make_object(data=data)


def get_experiment_metadata_by_id(metadata_id):
    """
    Fetch an existing metadata record for Excel-based experiment workflow ETL.

    :param metadata_id: the id of the metadata record
    :return: a object of :class:`materials_commons.api.EtlMetadata`
    """
    results = api.get_experiment_metadata(metadata_id)
    if _has_key('error', results):
        print("Error: ", results['error'])
        return None
    data = results['data']
    return make_object(data=data)


class User(MCObject):
    """
    Representing a registered user.

    .. note:: normally created from the database by a call to top level function :func:`mcapi.get_all_users`

    """

    def __init__(self, data=None):
        # normally, from the data base
        self.id = ""
        self.fullname = ""
        self.email = ""

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(User, self).__init__(data)

        attr = ['fullname', 'email']
        for a in attr:
            setattr(self, a, data.get(a, None))

    def can_access(self, project):
        """
        Does this user have permission to access the indicated project.

        :param project: an instance of the :class: `mcapi.Project`
        :return: boolean

        >>> user_list = get_all_users()
        >>> for user in user_list:
        >>>     if user.can_access(project):
        >>>         print(user.fullname, user.email)

        """
        user_ids = project.get_access_list()
        for id in user_ids:
            if id == self.id:
                return True
        return False


class Experiment(MCObject):
    """
    A Materials Commons Experiment.

    .. note:: normally created from database by by a call to :func:`mcapi.Project.create_experiment`

    """

    def __init__(self, project_id=None, name=None, description=None,
                 data=None):
        self.id = None  #: experiment id - string (from database)
        self.name = ""  #: experiment name - string (from database)
        self.description = ""  #: experiment description - string (from database)

        self.project_id = None
        self.project = None  #: the :class:`mcapi.Project` instance of the project that contains this experiment

        self.status = None  #: the status of the experiment - string
        self.funding = ''  #: funding description - string
        self.note = ''  #: any notes - string

        self.tasks = None
        self.publications = None  #: list of string
        self.notes = None  #: list of string
        self.papers = None  #: list of string
        self.collaborators = None  #: list of string
        self.citations = None  #: list of string
        self.goals = None  #: list of string
        self.aims = None  #: list of string

        self.category = None  #: string

        self.samples = []  #: list of :class:`mcapi.Sample` instances
        self.processes = {}  #: set of :class:`mcapi.Process` instances

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Experiment, self).__init__(data)

        attr = ['project_id', 'status', 'tasks', 'funding', 'publications',
                'notes', 'papers', 'collaborators', 'note', 'citations',
                'goals', 'aims']
        for a in attr:
            setattr(self, a, data.get(a, None))

        if name:
            self.name = name
        if description:
            self.description = description
        if project_id:
            self.project_id = project_id

        attr = ['tasks', 'publications', 'notes', 'collaborators', 'citations',
                'goals', 'aims']
        for a in attr:
            array = getattr(self, a)
            if not array:
                array = []
            setattr(self, a, array)

    def _process_special_objects(self):
        if self.samples:
            self.samples = [make_object(s.input_data) for s in self.samples]
        if self.processes:
            self.processes = [make_object(s.input_data) for s in self.processes]

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
        pp.write("id: " + self.id)
        pp.write("owner: " + pp.str(self.owner))

    # Experiment - basic methods: rename, put, delete

    def rename(self, name, description=None):
        """
        rename this experiment

        :param name:
        :param description:
        :return: this

        """
        project = self.project
        experiment = self
        if not description:
            description = self.description
        results = api.rename_experiment(project.id, experiment.id, name, description)
        if results:
            self.name = results['name']
            self.description = results['description']
        return self

    def put(self):
        """
        Copy local values to database.

        :return: this

        .. note:: Currently not implemented

        """
        # TODO: Experiment.put()
        raise NotImplementedError("Experiment.put() is not implemented")
        pass

    def delete(self):
        """
        Delete this Experiment from the database or (when dry_run is True)
        determine the objects to be deleted.

        :return: the id of the deleted experiment

        """
        api.delete_experiment(self.project.id, self.id)
        return self.id

    # Experiment - Process-related methods

    def create_process_from_template(self, template_id):
        """
        Create a process from a template

        :param template_id:
        :return: the :class:`mcapi.Process` instance

        >>> templates = get_all_templates()
        >>> template = None
        >>> for t in templates:
        >>>     if t.name == 'Create Samples':
        >>>         template = t
        >>> if template:
        >>>     create_sample_process = experiment.create_process_from_template(template.id)

        """
        project = self.project
        experiment = self
        results = api.create_process_from_template(project.id, experiment.id, template_id)
        process = make_object(results)
        process.project = project
        process.experiment = experiment
        process._update_project_experiment()
        return process

    def get_process_by_id(self, process_id):
        """
        Get a process for a given process id value.

        :param process_id:
        :return: the :class:`mcapi.Process` instance
        """
        project = self.project
        experiment = self
        results = api.get_experiment_process_by_id(project.id, experiment.id, process_id)
        process = make_object(results)
        process.project = project
        process.experiment = experiment
        process._update_project_experiment()
        return process

    def get_all_processes(self):
        """
        Get all the processes in this Experiment.

        :return: the list of :class:`mcapi.Process` instances

        """
        process_list = api.fetch_experiment_processes(self.project.id, self.id)
        processes = [make_object(x) for x in process_list]
        processes = [_decorate_object_with(x, 'project', self.project) for x in processes]
        processes = [_decorate_object_with(x, 'experiment', self) for x in processes]
        for process in processes:
            process._update_project_experiment()
        return processes

    # Experiment - Sample-related methods

    def get_sample_by_id(self, sample_id):
        """
        Get a Sample value from a sample id value.

        :param sample_id:
        :return: the :class:`mcapi.Sample` instance

        """
        project = self.project
        experiment = self
        results = api.get_experiment_sample_by_id(project.id, experiment.id, sample_id)
        sample = make_object(results)
        sample.project = project
        sample.experiment = experiment
        return sample

    def get_all_samples(self):
        """
        Get all samples in this Experiment.

        :return: the list of :class:`mcapi.Sample` instances

        """
        samples_list = api.fetch_experiment_samples(self.project.id, self.id)
        samples = [make_object(x) for x in samples_list]
        samples = [_decorate_object_with(x, 'project', self.project) for x in samples]
        samples = [_decorate_object_with(x, 'experiment', self) for x in samples]
        return samples

    # Experiment - additional method
    def decorate_with_samples(self):
        """
        Add all the Experiment's samples (from the database) into the local copy

        :return: this experiment with the instances of :class:mcapi.Sample added as the samples attribute

        >>> experiment = experiment.decorate_with_samples()
        >>> for sample in experiment.samples:
        >>>     print(sample.name)

        """
        self.samples = self.get_all_samples()
        return self

    def decorate_with_processes(self):
        """
        Add all the Experiment's processes (from the database) into the local copy

        :return: this experiment with the instances of :class:mcapi.Process added as the processes attribute

        >>> experiment = experiment.decorate_with_processes()
        >>> for process in experiment.processes:
        >>>     print(process.name)

        """
        self.processes = self.get_all_processes()
        return self


class Process(MCObject):
    """
    A Materials Commons Process.

    .. note:: Normally created from the database by a call to :func:`mcapi.Experiment.create_process_from_template`

    """

    def __init__(self, data=None):
        self.does_transform = False
        self.input_files = []  #: list of :class:`mcapi.File` instance
        self.output_files = []  #: list of :class:`mcapi.File` instance
        self.input_samples = []  #: list of :class:`mcapi.Sample` instance
        self.output_samples = []  #: list of :class:`mcapi.Sample` instance

        self.owner = ''
        self.setup = []
        self.measurements = []  #: list of :class:`mcapi.Measurement` instance
        self.transformed_samples = []  #: list of :class:`mcapi.Sample` instance
        self.what = ''  #: string
        self.why = ''  #: string
        self.category = None  #: string
        self.experiment = None  #: the :class:`mcapi.Experiment` containing this process

        self.project = None  #: the :class:`mcapi.Project` containing this process

        #: a derived dictionary of the setup properties of this process;
        #: a dictionary of :class:`mcapi.Property` with *key* = property.attribute;
        #: see :func:`mcapi.Process.get_setup_properties_as_dictionary`
        self.properties_dictionary = {}

        # filled in when Process is in Sample.processes

        #: 'in' or 'out' - filled in when process is in Sample.processes; see :class:`mcapi.Sample`
        self.direction = ''

        self.process_id = ''  #: string - filled in when process is in Sample.processes; see :class:`mcapi.Sample`
        self.sample_id = ''  #: string - filled in when process is in Sample.processes; see :class:`mcapi.Sample`
        self.property_set_id = ''  #: string - filled in when process is in Sample.processes; see :class:`mcapi.Sample`

        #: list of :class:`mcapi.Experiment` instances - filled in when process is in Sample.processes;
        #: see :class:`mcapi.Sample`
        self.experiments = []

        #: list of :class:`mcapi.Measurement` instances - filled in when measurements are attached
        self.measurements = []

        #: extra field for convenience; equivalent to description
        self.notes = ''

        self._files = []

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Process, self).__init__(data)

        attr = ['setup', 'category', 'process_type', 'does_transform', 'template_id', 'note',
                'template_name', 'direction', 'process_id', 'sample_id',
                'property_set_id']
        for a in attr:
            setattr(self, a, data.get(a, None))

        attr = ['measurements', 'output_samples', 'input_samples',
                'transformed_samples', 'experiments']
        for a in attr:
            setattr(self, a, data.get(a, []))

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
        # setup?
        # note?
        pp.write("description: " + pp.str(self.description))
        pp.write("id: " + pp.str(self.id))
        pp.write("owner: " + pp.str(self.owner))
        pp.write("template_id: " + pp.str(self.template_id))
        pp.write("template_name: " + pp.str(self.template_name))
        pp.write("does_transform: " + pp.str(self.does_transform))
        pp.write("process_type: " + pp.str(self.process_type))
        pp.write_objects("input_files: ", self.input_files)
        pp.write_objects("output_files: ", self.output_files)
        if hasattr(self, 'files'):
            pp.write_objects("files: ", self.files)
        pp.write_objects("input_samples: ", self.input_samples)
        pp.write_objects("output_samples: ", self.output_samples)
        if len(self.transformed_samples):
            pp.write_objects("transformed_samples: ", self.transformed_samples)
        if self.direction:
            pp.write("direction: " + pp.str(self.direction))
            pp.write("process_id: " + pp.str(self.process_id))
            pp.write("sample_id: " + pp.str(self.sample_id))
            pp.write("property_set_id: " + pp.str(self.property_set_id))
        if len(self.experiments):
            pp.write_objects("experiments: ", self.experiments)
        if len(self.measurements):
            pp.write_measurements(self.measurements)

    def _process_special_objects(self):
        super(Process, self)._process_special_objects()
        # self.notes = self.input_data['description']
        if self.setup:
            self.setup = [self._transform_setup(item) for item in self.setup]
        if self.measurements:
            self.measurements = [make_measurement_object(m) for m in self.measurements]
        if self.input_samples:
            self.input_samples = [make_object(s.input_data) for s in self.input_samples]
            for sample in self.input_samples:
                sample.project = self.project
                sample.experiment = self.experiment
        if self.output_samples:
            self.output_samples = [make_object(s.input_data) for s in self.output_samples]
            for sample in self.output_samples:
                sample.project = self.project
                sample.experiment = self.experiment
        if hasattr(self, 'filesLoaded') and not self.filesLoaded:
            del self.files

    def _update_project_experiment(self):
        for sample in self.input_samples:
            sample.project = self.project
            sample.experiment = self.experiment

        for sample in self.output_samples:
            sample.project = self.project
            sample.experiment = self.experiment

        for sample in self.transformed_samples:
            sample.project = self.project
            sample.experiment = self.experiment

        for file in self.input_files:
            file.project = self.project
            file.experiment = self.experiment

        for file in self.output_files:
            file.project = self.project
            file.experiment = self.experiment

    def _transform_setup(self, setup_element):
        setup_element.properties = [self._transform_property(prop) for prop in setup_element.properties]
        return setup_element

    def _transform_property(self, process_property):
        prop = make_property_object(process_property)
        return prop

    # Process - basic methods: rename, put, delete

    def rename(self, process_name):
        """
        Rename this process.

        :param process_name: new name - string
        :return: the updated :class:`mcapi.Process`

        """
        results = api.push_name_for_process(self.project.id, self.id, process_name)
        process = make_object(results)
        process.project = self.project
        process.experiment = self.experiment
        process._update_project_experiment()
        return process

    def delete(self):
        """
        Delete this process. The process is removed from the database leaving only the local copy.
        A process can not be deleted if any of the following are true: (1) it is not a leaf node in
        the workflow, (2) is is in a dataset, (3) it is a create sample (type) process with one or
        more output samples.

        :return: id - the id of the process deleted or None (if the process was not deleted)

        """
        process_with_outputs = self.decorate_with_output_samples()
        process_create = \
            (process_with_outputs.process_type == 'create'
             or process_with_outputs.template_name == 'Sectioning')
        if process_create and (len(process_with_outputs.output_samples) > 0):
            return None

        results = None
        try:
            results = api.delete_process(self.project.id, self.id)
            if 'error' in results:
                results = None
            else:
                results = results['id']
        except Exception:
            pass

        return results

    def put(self):
        """
        Copy local values to database.

        :return: this

        .. note:: Currently not implemented

        """
        # TODO Process.put()
        raise NotImplementedError("Process.put() is not implemented")
        pass

    # Process - additional basic methods
    def set_notes(self, note_text):
        note_text = "<p>" + note_text + "</p>"
        results = api.set_notes_for_process(self.project.id, self.id, note_text)
        process = make_object(results)
        process.project = self.project
        process.experiment = self.experiment
        process._update_project_experiment()
        process.notes = process.description
        return process

    def add_to_notes(self, note_text):
        note_text = self.notes + "\n<p>" + note_text + "</p>"
        results = api.set_notes_for_process(self.project.id, self.id, note_text)
        process = make_object(results)
        process.project = self.project
        process.experiment = self.experiment
        process._update_project_experiment()
        process.notes = process.description
        return process

    # Process - Sample-related methods - create, get_by_id, get_all
    def create_samples(self, sample_names):
        """
        Create output samples for this process.

        .. note:: this function only works for processes with process_type == 'create' or with
            the 'sectioning' process (that is template_name == 'sectioning').

        :param sample_names: a list of string
        :return: a list of :class:`mcapi.Sample`

        """
        process_ok = (self.process_type == 'create' or self.template_name == 'Sectioning')
        if not process_ok:
            print("Either Process.process_type is not 'create' or " +
                  "Process.template_name is not 'sectioning'; instead: " +
                  "process_type == " + self.process_type + " and " +
                  "template_name == " + self.template_name + " -- returning None")
            # throw exception?
            return None
        samples = self._create_samples(sample_names)
        self.decorate_with_output_samples()
        ret_samples = []
        for s in samples:
            for probe in self.output_samples:
                if s.id == probe.id:
                    ret_samples.append(probe)
        return ret_samples

    def get_sample_by_id(self, process_id):
        """
        Get indicated Sample.

        :param process_id: sample if - string
        :return: a :class:`mcapi.Sample` instance

        .. note:: Currently not implemented

        """
        # TODO: Process.get_sample_by_id(id)
        raise NotImplementedError("Process.get_sample_by_id(id) is not implemented")
        pass

    def get_all_samples(self):
        """
        Get all samples for the process.

        :return: a list of :class:`mcapi.Sample` instances

        """
        input_samples = self.input_samples
        output_samples = self.output_samples
        return input_samples + output_samples

    def add_input_samples_to_process(self, samples):
        """
        Add input samples to this process.

        :param samples: a list of :class:`mcapi.Sample` instances
        :return: the updated process

        """
        return self._add_input_samples_to_process(samples)

    # Process - File-related methods - truncated?
    # TODO: should Process have File-related create, get_by_id, get_all?
    def get_all_files(self):
        """
        Get the list of files for this process.

        :return: files_list: a list of :class:`mcapi.File` instances

        """
        project = self.project
        experiment = self.experiment
        process = self
        results = api.get_all_files_for_process(project.id, experiment.id, process.id)
        file_list = [make_object(x) for x in results]
        return file_list

    def add_files(self, files_list):
        """
        Add files to this process.

        :param files_list: a list of :class:`mcapi.File` instances
        :return: the updated process

        """
        return self._add_files_to_process(files_list)

    # Process - SetupProperties-related methods - special methods
    def get_setup_properties_as_dictionary(self):
        """
        Create a 'helper' dictionary of the properties of this Process.
        See :class:`mcapi.Property`

        :return: look-up dictionary keyed by the Property.attribute

        """
        if self.properties_dictionary:
            return self.properties_dictionary
        ret = {}
        for s in self.setup:
            props = s.properties
            for prop in props:
                prop.setup_attribute = s.attribute
                ret[prop.attribute] = prop
        self.properties_dictionary = ret
        return ret

    def is_known_setup_property(self, attribute):
        """
        Determine if the attribute is a, template-supported, known property of this process.

        :param attribute: A string, the attribute key
        :return: True, False
        """
        return attribute in self.get_setup_properties_as_dictionary()

    def set_value_of_setup_property(self, name, value):
        """
        Populate, locally, the template-supported set-up property indicated by *name*, with a value for that property.

        :param name: string
        :param value: any
        :return: None
        """
        prop = self.get_setup_properties_as_dictionary()[name]
        if prop:
            prop.verify_value_type(value)
            prop.value = value
        else:
            raise MCPropertyException("Property '" + name + "' is not defined for this process template")

    def set_unit_of_setup_property(self, name, unit):
        """
        Augment, locally, the template-supported set-up property indicated by *name*, with a unit type for that property.

        :param name: - string
        :param unit: - unit type - string
        :return: None
        """
        prop = self.get_setup_properties_as_dictionary()[name]
        if prop:
            if unit in prop.units:
                prop.unit = unit
            elif not prop.unit:  # Note prop.unit may be preloaded
                message = "' there is no unit selection '" + unit + "'"
                message += ", acceptable units are: " + ",".join(prop.units)
                raise MCPropertyException("For property '" + name + message)
            elif unit != prop.unit:
                # Note prop.unit may be preloaded
                message = "' the unit value '" + unit + "'"
                message += " does not match the expected value " + prop.unit
                raise MCPropertyException("For property '" + name + message)

        else:
            raise MCPropertyException("Property '" + name + "' is not defined for this process template")

    def update_setup_properties(self, name_list):
        """
        For local template-supported set-up properties indicated by *name_list*,
        push (to the database) those properties as set-up properties,
        ppreciously augmented locally for this process.

        :param name_list: list of string
        :return: the updated process

        """
        prop_dict = self.get_setup_properties_as_dictionary()
        prop_list = []
        for name in name_list:
            prop = prop_dict[name]
            if prop:
                prop_list.append(prop)
        return self._update_process_setup_properties(prop_list)

    def update_additional_setup_properties(self, entry_list):
        """
        Use parameters in entry_list to add parameter values to this process (in the database).
        Intended for parameter values that are not in the template for this process.
        (Currently, the object types supported are: 'string' and 'number'. The 'otype' is not
        required, The default will be based on the type of value.)

        :param entry_list: a list of objects: [{name: name, attribute: attribute, value: value, unit: unit, otype: object-type}, ...]
        :return: the updated process
        """
        args = []
        for e in entry_list:
            if "name" not in e and 'attribute' not in e:
                print("This additional parameter is missing both 'name' and 'attribute' "
                      "at least one of which is required, skipping", e)
                continue
            if "value" not in e:
                print("This additional parameter does not have 'value' specified, skipping", e)
                continue
            if 'name' in e and 'attribute' not in e:
                e['attribute'] = _normalise_property_name(e['name'])
            if 'attribute' in e and 'name' not in e:
                e['name'] = e['attribute']
            e['attribute'] = _normalise_property_name(e['attribute'])
            probe = _convert_for_json_if_datetime(e['value'])
            if probe:
                e['otype'] = 'date'
                e['value'] = probe
            if 'otype' not in e:
                try:
                    value = float(str(e['value']))
                    e['otype'] = 'number'
                    e['value'] = value
                except ValueError:
                    e['otype'] = 'string'
            if e['otype'] == 'string':
                e['value'] = str(e['value'])
            args.append(e)
        if args:
            ret = api.update_additional_properties_in_process(self.project.id, self.experiment.id, self.id, args)
            updated = make_object(ret['val'])
            self.setup = updated.setup
        return self

    def make_list_of_samples_for_measurement(self, samples):
        '''
        Augment samples with setup properties from this process; the samples must have been created by the process;
        see :func:`mcapi.Process.create_sample`

        :param samples: list of :class:`mcapi.Sample` instances
        :return: list of :class:`mcapi.Sample` instances with their property_set id values set

        '''
        process_measurement_samples = self.get_all_samples()
        filter = "in"
        if self.process_type == 'transform' or self.process_type == 'create':
            filter = "out"
        process_measurement_samples = [s for s in process_measurement_samples if s.direction == filter]
        if not process_measurement_samples:
            return []

        results = []
        checked_sample_list = []
        for sample in process_measurement_samples:
            check_sample = None
            for s in samples:
                if s.id == sample.id:
                    check_sample = s
                    break
            if check_sample:
                checked_sample_list.append(check_sample)
        if not checked_sample_list:
            return results

        for sample in checked_sample_list:
            results.append({
                'property_set_id': sample.property_set_id,
                'sample': sample
            })

        return results

    # Process - Measurement-related methods - special treatment

    def create_measurement(self, data):
        """

        :param data: dictionary - measurement data, see example
            below at :func:`mcapi.Process.set_measurements_for_process_samples`
        :return: the appropriate :class:`mcapi.Measurement` subclass

        """
        return make_measurement_object(data)

    def set_measurements_for_process_samples(self, measurement_property, measurements):
        """
        Set a measurement for the indicated *measurement_property*.

        :param measurement_property: dictionary - the property, see example below
        :param measurements: :class:`mcapi.Measurement`
        :return: the updated Process value

        >>> measurement_data = {
        >>>     "name": "Composition",
        >>>     "attribute": "composition",
        >>>     "otype": "composition",
        >>>     "unit": "at%",
        >>>     "value": [
        >>>         {"element": "Al", "value": 94},
        >>>         {"element": "Ca", "value": 1},
        >>>         {"element": "Zr", "value": 5}],
        >>>     "is_best_measure": True
        >>> }
        >>> measurement = my_process.create_measurement(data=measurement_data)
        >>>
        >>> measurement_property = {
        >>>     "name": "Composition",
        >>>     "attribute": "composition"
        >>> }
        >>> my_process = my_process.set_measurements_for_process_samples(measurement_property, [measurement])

        """
        return self._set_measurement_for_process_samples(
            self.make_list_of_samples_for_measurement(self.get_all_samples()),
            measurement_property,
            measurements
        )

    def set_measurement(self, attribute, measurement_data, name=None):
        """
        A low-level function for adding a measurement to the output samples of this process.

        :param attribute: string - the measurement attribute
        :param measurement_data: - an dictionary with the name-value pairs for the measurement
        :param name: (optional) string - if not given the name=attribute
        :return: the updated process

        """
        if not name:
            name = attribute

        if "name" not in measurement_data:
            measurement_data['name'] = name

        if "attribute" not in measurement_data:
            measurement_data['attribute'] = attribute

        if "unit" not in measurement_data:
            measurement_data['unit'] = ""

        measurement = self.create_measurement(data=measurement_data)

        measurement_property = {
            "name": name,
            "attribute": attribute
        }

        return self.set_measurements_for_process_samples(
            measurement_property, [measurement])

    def add_integer_measurement(self, attrname, value, name=None):
        """
        A helper function to add integer measurements to the output samples of this process.

        :param attrname: the name of the attribute - string
        :param value: - integer
        :param name: - (optional) string - if not given the name=attribute
        :return: the updated process
        """
        if not name:
            name = attrname

        measurement_data = {
            "name": name,
            "attribute": attrname,
            "otype": "integer",
            "value": value,
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_number_measurement(self, attrname, value, name=None):
        """

        :param attrname: - string
        :param value: - number
        :param name: - (optional) string - if not given the name=attribute
        :return: the updated process
        """
        measurement_data = {
            "attribute": attrname,
            "otype": "number",
            "value": value,
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_boolean_measurement(self, attrname, value, name=None):
        """

        :param attrname: - string
        :param value: - boolean (True or False)
        :param name: - (optional) string - if not given the name=attribute
        :return: the updated process
        """
        measurement_data = {
            "attribute": attrname,
            "otype": "boolean",
            "value": value,
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_string_measurement(self, attrname, value, name=None):
        """

        :param attrname: - string
        :param value: - string
        :param name: - (optional) string - if not given the name=attribute
        :return: the updated process
        """
        measurement_data = {
            "attribute": attrname,
            "otype": "string",
            "value": value,
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_file_measurement(self, attrname, file, name=None):
        """

        :param attrname: - string
        :param file: a :class:`mcapi.File` instance
        :param name: - (optional) string - if not given the name=attribute
        :return: the updated process
        """
        measurement_data = {
            "attribute": attrname,
            "otype": "file",
            "value": {
                "file_id": file.id,
                "file_name": file.name
            },
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    # NOTE: no covering test or example for this function - probably works - Terry, Jan 20, 2016
    # TODO: add covering test for add_sample_measurement
    def add_sample_measurement(self, attrname, sample, name=None):
        """

        :param attrname: - string
        :param sample: a :class:`mcapi.Sample` instance
        :param name: - (optional) string - if not given the name=attribute
        :return: the updated process
        """
        measurement_data = {
            "attribute": attrname,
            "otype": "sample",
            "value": {
                "sample_id": sample.id,
                "sample_name": sample.name,
                "property_set_id": sample.property_set_id
            },
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_list_measurement(self, attrname, value, value_type, name=None):
        """

        :param attrname: - string
        :param value: - a list in which all the objects are the same type
        :param value_type: - string, the type of the objects in the list
        :param name: - (optional) string - if not given the name=attribute
        :return: the updated process
        """
        measurement_data = {
            "attribute": attrname,
            "otype": "vector",
            "value": {
                "dimensions": len(value),
                "otype": value_type,
                "value": value
            },
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_numpy_matrix_measurement(self, attrname, value, name=None):
        """

        :param attrname: - string
        :param value: - a numpy Matrix
        :param name: - (optional) string - if not given the name=attribute
        :return: the updated process
        """
        measurement_data = {
            "attribute": attrname,
            "otype": "matrix",
            "value": {
                "dimensions": list(value.shape),
                "otype": "float",
                "value": value.tolist()
            },
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_selection_measurement(self, attrname, value, name=None):
        """

        :param attrname: - string
        :param value: one of the choices in a selection
        :param name: - (optional) string - if not given the name=attribute
        :return: the updated process
        """
        measurement_data = {
            "attribute": attrname,
            "otype": "selection",
            "value": value,
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    def add_vector_measurement(self, attrname, value, name=None):
        """

        :param attrname: - string
        :param value: - a list of float values
        :param name: - (optional) string - if not given the name=attribute
        :return: the updated process
        """
        measurement_data = {
            "attribute": attrname,
            "otype": "vector",
            "value": {
                "dimensions": len(value),
                "otype": "float",
                "value": value
            },
            "is_best_measure": True
        }
        return self.set_measurement(attrname, measurement_data, name)

    # Process - additional methods
    def decorate_with_output_samples(self):
        """
        Make sure that known output samples are set in the this.

        :return: a new copy of the Process (this) with the addition of output samples from the database
        """
        detailed_process = self.experiment.get_process_by_id(self.id)
        self.output_samples = detailed_process.output_samples
        return self

    def decorate_with_input_samples(self):
        """
        Make sure that known input samples are set in this.

        :return: a new copy of the Process (this) with the addition of input samples from the database
        """
        detailed_process = self.experiment.get_process_by_id(self.id)
        self.input_samples = detailed_process.input_samples
        return self

    # Process - internal (private method)
    def _set_measurement_for_process_samples(self, samples_with_property_set_ids, measurement_property, measurements):
        project_id = self.project.id
        experiment_id = self.experiment.id
        process_id = self.id
        samples_parameter = []
        for table in samples_with_property_set_ids:
            samples_parameter.append({
                'id': table['sample'].id,
                'property_set_id': table['property_set_id']
            })
        measurement_parameter = []
        for measurement in measurements:
            measurement_parameter.append({
                'name': measurement.name,
                'attribute': measurement.attribute,
                'otype': measurement.otype,
                'value': measurement.value,
                'unit': measurement.unit,
                'is_best_measure': measurement.is_best_measure
            })
        success_flag = api.set_measurement_for_process_samples(
            project_id, experiment_id, process_id,
            samples_parameter, measurement_property, measurement_parameter)
        if not success_flag:
            print("mcapi.mc._set_measurement_for_process_samples - unexpectedly failed")
            return None
        return self.experiment.get_process_by_id(process_id)

    def _add_input_samples_to_process(self, samples):
        project = self.project
        experiment = self.experiment
        process = self
        results = api.add_samples_to_process(project.id, experiment.id, process, samples)
        new_process = make_object(results)
        for sample in new_process.input_samples:
            sample.experiment = experiment
            sample.project = project
            found_sample = None
            for existing_sample in process.input_samples:
                if existing_sample.id == sample.id:
                    found_sample = existing_sample
            if not found_sample:
                process.input_samples.append(sample)
        process.project = project
        process.experiment = experiment
        process._update_project_experiment()
        return process

    def _add_files_to_process(self, file_list):
        project = self.project
        experiment = self.experiment
        process = self
        results = api.add_files_to_process(project.id, experiment.id, process, file_list)
        process = make_object(results)
        process.project = project
        process.experiment = experiment
        process._update_project_experiment()
        return process

    def _update_process_setup_properties(self, prop_list):
        project = self.project
        experiment = self.experiment
        process = self
        results = api.update_process_setup_properties(
            project.id, experiment.id, process, prop_list)
        process = make_object(results)
        process.project = project
        process.experiment = experiment
        process._update_project_experiment()
        return process

    def _create_samples(self, sample_names):
        project = self.project
        process = self
        samples_array_dict = api.create_samples_in_project(project.id, process.id, sample_names)
        samples_array = samples_array_dict['samples']
        # NOTE: in this case, for this version of API, for the call implemented, the
        # returned object is very sparse; hence the samples need to be re-fetched...
        # however, the fetched object is missing the property_set_id, to add it..
        lookup_table = {}
        for simple_sample in samples_array:
            lookup_table[simple_sample['id']] = simple_sample['property_set_id']
        samples = [project.fetch_sample_by_id(x['id']) for x in samples_array]
        samples = [_decorate_object_with(x, 'property_set_id', lookup_table[x.id]) for x in samples]
        samples = [_decorate_object_with(x, 'project', project) for x in samples]
        samples = [_decorate_object_with(x, 'experiment', process.experiment) for x in samples]
        samples_id_list = []
        # NOTE: side effect to process.experiment
        for sample in samples:
            samples_id_list.append(sample.id)
            sample_in_experiment = None
            for s in process.experiment.samples:
                if sample.id == s.id:
                    sample_in_experiment = s
            if not sample_in_experiment:
                process.experiment.samples.append(sample)
        api.add_samples_to_experiment(project.id, process.experiment.id, samples_id_list)
        return samples


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
    def rename(self, name):
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
            results = None
            try:
                results = api.delete_sample_created_by_process(self.project.id, proc_id, self.id, property_set_id)
                if 'error' in results:
                    results = None
            except Exception:
                pass

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
        api.link_files_to_sample(self.project.id, self.id, id_list)
        return self.update_with_details()

    def update_with_details(self):
        updated_sample = self.project.fetch_sample_by_id(self.id)
        updated_sample.project = self.project
        updated_sample.experiment = self.experiment
        return updated_sample

    def decorate_with_processes(self):
        filled_in_sample = make_object(api.fetch_sample_details(self.project.id, self.id))
        self.processes = filled_in_sample.processes
        return self


class Directory(MCObject):
    """
    A Materials Commons Directory.

    .. note:: normally created from the database by call to :func:`mcapi.Project.add_directory` or
        any of the project methods that create directories on a given path

    """

    def __init__(self, name="", path="", data=None):
        # normally, from the data base
        self.id = ""  #: directory id
        self.name = ""  #: directory name
        self.checksum = ""
        self.path = ""  #: directory path within project
        self.size = 0

        # additional fields
        self._project = None
        self._parent_id = None

        # NOTE: children are not stored locally, but always fetch from remote!
        # see self.getChild(name)

        if not data:
            data = {}

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Directory, self).__init__(data)

        attr = ['checksum', 'path', 'size']
        for a in attr:
            setattr(self, a, data.get(a, None))

        # kw args
        if name:
            self.name = name
        if path:
            self.path = path

    def _process_special_objects(self):
        data = self.input_data
        if not data:
            return
        if _has_key('parent', data):
            self._parent_id = data['parent']

    # directory - basic methods: rename, move, put, delete
    def rename(self, new_name):
        """
        Rename this directory. Top level directory, can not be renamed, rename project instead.
        :param new_name: string
        :return: updated directory
        """
        dir_data = api.directory_rename(self._project.id, self.id, new_name)
        updated_directory = make_object(dir_data)
        updated_directory._project = self._project
        return updated_directory

    def move(self, new_parent_directory):
        """
        Move this directory into another directory. Changes the path of this
        directory and the contents of the new parent directory.

        :param new_parent_directory: an instance of :class:`mcapi.Directory`
        :return:
        """
        project_id = self._project.id
        new_directory_id = new_parent_directory.id
        results = api.directory_move(project_id, self.id, new_parent_directory.id)
        updated_directory = make_object(results)
        updated_directory._project = self._project
        if not updated_directory._parent_id:
            updated_directory._parent_id = new_directory_id
        return updated_directory

    def put(self):
        """
        Copy local values to database.

        :return: this

        .. note:: Currently not implemented

        """
        # TODO Directory.put()
        pass

    def delete(self):
        """
        Delete this directory.

        :return: None

        .. note:: Currently not implemented

        """
        # TODO Directory.delete() ?? only when empty
        raise NotImplementedError("Directory.delete() is not implemented")
        pass

    def get_children(self):
        from .File import File
        """
        Get the contents of this directory.

        :return: a list of :class:`mcapi.Directory` and/or :class:`mcapi.File` instances

        """
        results = api.directory_by_id(self._project.id, self.id)
        ret = []
        for dir_or_file in results['children']:
            its_type = dir_or_file['otype']
            if its_type == 'file':
                obj = File(data=dir_or_file)
                obj._directory_id = self.id
            if its_type == 'directory':
                obj = Directory(data=dir_or_file)
                obj._parent_id = self.id
            obj._project = self._project
            ret.append(obj)
        return ret

    def create_descendant_list_by_path(self, path):
        """
        Create any directories missing on the given path, relative to this directory, and return all the
        directories on the path.

        :param path: string
        :return: a list of :class:`mcapi.Directory` instances
        """
        results = api.create_fetch_all_directories_on_path(self._project.id, self.id, path)
        dir_list = []
        parent = self
        for dir_data in results['dirs']:
            directory = make_object(dir_data)
            directory._project = self._project
            if not directory._parent_id:
                directory._parent_id = parent.id
            parent = directory
            dir_list.append(directory)
        return dir_list

    def get_descendant_list_by_path(self, path):
        """
        Return all the directories on the given path, relative to this directory; if any are missing
        and error is generated.

        :param path: string
        :return: a list of :class:`mcapi.Directory` instances
        """
        all_directories = self._project.get_all_directories()
        dir_list = []
        parent = self
        full_path = self._project.name + path
        for directory in all_directories:
            dir_path = directory.name
            if full_path.startswith(dir_path):
                directory = self._project.get_directory(directory.id)
                if not directory._parent_id:
                    directory._parent_id = parent.id
                parent = directory
                dir_list.append(directory)
        return dir_list

    def add_file(self, file_name, local_input_path, verbose=False, limit=50):
        """
        Upload local file, and attach it to an new file in this directory.

        :param file_name: name of the new file - string
        :param local_input_path: path to the local file - string
        :param verbose: (optional) flag to print()trace of all actions - True or False
        :param limit: (optional) the limit in MB of the size of the file to upload
        :return: an instance of :class:`mcapi.File` - the new file
        """
        result = self._project.add_file_using_directory(self, file_name, local_input_path, verbose, limit)
        return result

    def add_directory_tree(self, dir_name, input_dir_path, verbose=False, limit=50):
        """
        Given the path to a local directory, create that directory path in the database,
        loading all the files in the tree.

        :param dir_name:
        :param input_dir_path:
        :param verbose:
        :param limit:
        :return:
        """
        if not os_path.isdir(input_dir_path):
            return None
        if verbose:
            name = self.path
            if self.shallow:
                name = self.name
            print("base directory: ", name)
        dir_tree_table = _make_dir_tree_table(input_dir_path, dir_name, dir_name, {})
        result = []
        error = {}
        for relative_dir_path in dir_tree_table.keys():
            file_dict = dir_tree_table[relative_dir_path]
            dirs = self.create_descendant_list_by_path(relative_dir_path)
            if verbose:
                print("relative directory: ", relative_dir_path)
            directory = dirs[-1]
            for file_name in file_dict.keys():
                input_path = file_dict[file_name]
                try:
                    result.append(directory.add_file(file_name, input_path, verbose, limit))
                except Exception as e:
                    error[input_path] = e
        return result, error


# -- helper function for Directory.add_directory_tree - above
def _make_dir_tree_table(base_path, dir_name, relative_base, table_so_far):
    local_path = os_path.join(base_path, dir_name)
    file_dictionary = {}
    for data_file in listdir(local_path):
        path = os_path.join(local_path, data_file)
        if os_path.isfile(path):
            file_dictionary[data_file] = path
    table_so_far[relative_base] = file_dictionary
    for directory in listdir(local_path):
        path = os_path.join(local_path, directory)
        base = os_path.join(relative_base, directory)
        if os_path.isdir(path):
            table_so_far = _make_dir_tree_table(local_path, directory, base, table_so_far)
    return table_so_far


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

        attr = ['experiment_id', 'json']
        for a in attr:
            setattr(self, a, data.get(a, None))

    def _process_special_objects(self):
        # undo the effect of general object processing on the json data
        self.json = self.input_data['json']

    def update(self, new_metadata):
        results = api.update_experiment_metadata(self.id, new_metadata)
        if _has_key('error', results):
            print("Error: ", results['error'])
            return None
        data = results['data']
        updated_metadata_record = make_object(data=data)
        self.json = updated_metadata_record.json
        return self

    def delete(self):
        return api.delete_experiment_metadata(self.id)


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
        '''

        :param value:
        :return: None
        :raises: MCPropertyException when value does not match type
        '''
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


class MCPropertyException(BaseException):
    pass


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
            if (isinstance(value['name'], str) or isinstance(value['name'], unicode)) \
                    and (isinstance(value['value'], str) or isinstance(value['value'], unicode)):
                return
        if not isinstance(value, str):
            message = "Only str/unicode values for a SelectionProperty; "
            message += "value = '" + str(value) + "', type = " + str(type(value)) + " is not valid"
            raise MCPropertyException(message)
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
        if not value:
            _value = value
            return
        found = None
        for choice in self.choices:
            if value == choice['name'] or value == choice['value']:
                found = choice
                break
        if not found:
            self.verify_value_type(value)
            found = value
        self._value = found


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
