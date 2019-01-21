import sys

from . import api
from .base import MCObject, PrettyPrint
from .base import _decorate_object_with
from .make_objects import make_object, make_property_object
from .measurement import make_measurement_object
from .property import _normalise_property_name, _convert_for_json_if_datetime
from .property import MCPropertyException


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
        self.transformed_samples = []  #: list of :class:`mcapi.Sample` instance
        self.measurements = []  #: list of :class:`mcapi.Measurement` instance

        self.owner = ''
        self.setup = []
        self.what = ''  #: string
        self.why = ''  #: string
        self.category = None  #: string
        self.process_type = None
        self.template_id = ''
        self.template_name = ''

        self.experiment = None  #: the :class:`mcapi.Experiment` containing this process

        self.project = None  #: the :class:`mcapi.Project` containing this process

        #: a derived dictionary of the setup properties of this process;
        #: a dictionary of :class:`mcapi.Property` with *key* = property.attribute;
        #: see :func:`mcapi.Process.get_setup_properties_as_dictionary`
        self.properties_dictionary = {}

        # filled in when Process is in Sample.processes

        #: 'in' or 'out' - filled in when process is in Sample.processes; see :class:`mcapi.Sample`
        self.direction = ''

        self.template_id = ''  #: string - filled in when process is initialized`
        self.template_name = ''  #: string - filled in when process is initialized`
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

        self.files = []

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

    @staticmethod
    def _transform_property(process_property):
        prop = make_property_object(process_property)
        return prop

    # Process - basic methods: rename, put, delete

    def rename(self, process_name):
        """
        Rename this process.

        :param process_name: new name - string
        :return: the updated :class:`mcapi.Process`

        """
        results = api.push_name_for_process(self.project.id, self.id, process_name, apikey=self.project._apikey)
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
            results = api.delete_process(self.project.id, self.id, apikey=self.project._apikey)
            if 'error' in results:
                results = None
            else:
                results = results['id']
        except BaseException:
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
        results = api.set_notes_for_process(self.project.id, self.id, note_text, apikey=self.project._apikey)
        process = make_object(results)
        process.project = self.project
        process.experiment = self.experiment
        process._update_project_experiment()
        process.notes = process.description
        return process

    def add_to_notes(self, note_text):
        note_text = self.notes + "\n<p>" + note_text + "</p>"
        results = api.set_notes_for_process(self.project.id, self.id, note_text, apikey=self.project._apikey)
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

    def get_sample_by_id(self, sample_id):
        """
        Get indicated Sample.

        :param sample_id: the id of the sample - string
        :return: a :class:`mcapi.Sample` instance

        .. note:: Currently not implemented

        """
        # TODO: Process.get_sample_by_id(id)
        message = "Process.get_sample_by_id({}) is not implemented".format(process_id)
        raise NotImplementedError(message)
        pass

    def get_all_samples(self):
        """
        Get all samples for the process.

        :return: a list of :class:`mcapi.Sample` instances

        """
        input_samples = self.input_samples
        output_samples = self.output_samples
        return input_samples + output_samples

    def add_input_samples_to_process(self, samples, transform=None):
        """
        Add input samples to this process.

        :param samples: a list of :class:`mcapi.Sample` instances
        :param transform: (optional, default = None), a True/False flag to indicate that
            the output samples should be (automaticially) generated for transform-type
            processes. The normal behavior, without the flag, is for the output samples
            to be generate.
        :return: the updated process

        """
        return self._add_input_samples_to_process(samples, transform=transform)

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
        results = api.get_all_files_for_process(project.id, experiment.id, process.id, apikey=self.project._apikey)
        file_list = [make_object(x) for x in results]
        return file_list

    def add_files(self, files_list, direction=None):
        """
        Add files to this process.

        :param files_list: a list of :class:`mcapi.File` instances
        :param direction: (optional - default unset) 'in' or 'out' -
            set the indicated direction of the file with respect to the process
        :return: the updated process

        """
        return self._add_files_to_process(files_list, direction=direction)

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
        Augment, locally, the template-supported set-up property indicated
        by *name*, with a unit type for that property.

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
        probe = prop_list[0]
        return self._update_process_setup_properties(prop_list)

    def update_additional_setup_properties(self, entry_list):
        """
        Use parameters in entry_list to add parameter values to this process (in the database).
        Intended for parameter values that are not in the template for this process.
        (Currently, the object types supported are: 'string' and 'number'. The 'otype' is not
        required, The default will be based on the type of value.)

        :param entry_list: a list of objects: [{name: name,
            attribute: attribute, value: value, unit: unit, otype: object-type}, ...]
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
            ret = api.update_additional_properties_in_process(
                self.project.id, self.experiment.id, self.id, args, apikey=self.project._apikey)
            updated = make_object(ret['val'])
            self.setup = updated.setup
        return self

    def make_list_of_samples_for_measurement(self, samples):
        """
        Augment samples with setup properties from this process;
        the samples must have been created by the process;
        see :func:`mcapi.Process.create_sample`

        :param samples: list of :class:`mcapi.Sample` instances
        :return: list of :class:`mcapi.Sample` instances with their
            property_set id values set

        """
        process_measurement_samples = self.get_all_samples()
        direction_filter = "in"
        if self.process_type == 'transform' or self.process_type == 'create':
            direction_filter = "out"
        process_measurement_samples = [s for s in process_measurement_samples if s.direction == direction_filter]
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
    @staticmethod
    def create_measurement(data):
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
        Make sure that known output samples are set in the this Process.

        :return: the Process (this) with the addition of output samples from the database
        """
        detailed_process = self.experiment.get_process_by_id(self.id)
        self.output_samples = detailed_process.output_samples
        return self

    def decorate_with_input_samples(self):
        """
        Make sure that known input samples are set in this Process.

        :return: the Process (this) with the addition of input samples from the database
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
            samples_parameter, measurement_property, measurement_parameter,
            apikey=self.project._apikey)
        if not success_flag:
            print("mcapi.mc._set_measurement_for_process_samples - unexpectedly failed")
            return None
        return self.experiment.get_process_by_id(process_id)

    def _add_input_samples_to_process(self, samples, transform=None):
        project = self.project
        experiment = self.experiment
        process = self
        arg_list = [{'sample_id': s.id, 'property_set_id': s.property_set_id} for s in samples]
        if not transform is None:
            for ap in arg_list:
                ap['transform'] = transform
        results = api.add_samples_to_process(
            project.id, experiment.id, process.id, process.template_id, arg_list, apikey=self.project._apikey)
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

    def _add_files_to_process(self, file_list, direction=None):
        project = self.project
        experiment = self.experiment
        process = self
        file_ids = [file.id for file in file_list]
        results = api.add_files_to_process(
            project.id, experiment.id, process.id, process.template_id,
            file_ids, direction, apikey=self.project._apikey)
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
            project.id, experiment.id, process, prop_list, apikey=self.project._apikey)
        process = make_object(results)
        process.project = project
        process.experiment = experiment
        process._update_project_experiment()
        return process

    def _create_samples(self, sample_names):
        project = self.project
        process = self
        samples_array_dict = api.create_samples_in_project(
            project.id, process.id, sample_names, apikey=self.project._apikey)
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
        api.add_samples_to_experiment(project.id, process.experiment.id, samples_id_list, apikey=self.project._apikey)
        return samples
