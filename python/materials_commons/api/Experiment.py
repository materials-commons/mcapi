import sys

from . import api
from .base import MCObject, PrettyPrint
from .base import _decorate_object_with
from .make_objects import make_object
from .top_level_api_functions import get_all_templates


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
        rename this experiment; optionally change the description - defaults to the previous description.

        :param name:
        :param description:
        :return: this

        """
        project = self.project
        experiment = self
        if not description:
            description = self.description
        results = api.rename_experiment(project.id, experiment.id, name, description, apikey=project._apikey)
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
        api.delete_experiment(self.project.id, self.id, apikey=self.project._apikey)
        return self.id

    # Experiment - Process-related methods

    def create_process_from_template(self, template_id):
        """
        Create a process from a template

        :param template_id:
        :return: the :class:`mcapi.Process` instance

        >>> from materials_commons.api import get_all_templates
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
        results = api.create_process_from_template(project.id, experiment.id, template_id, apikey=project._apikey)
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
        results = api.get_experiment_process_by_id(project.id, experiment.id, process_id, apikey=project._apikey)
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
        process_list = api.fetch_experiment_processes(self.project.id, self.id, apikey=self.project._apikey)
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
        samples = self.get_all_samples()
        sample = None
        for probe in samples:
            if sample_id == probe.id:
                sample = probe
        if sample:
            sample.project = project
            sample.experiment = experiment
        return sample

    def get_all_samples(self):
        """
        Get all samples in this Experiment.

        :return: the list of :class:`mcapi.Sample` instances

        """
        samples_list = api.fetch_experiment_samples(self.project.id, self.id, apikey=self.project._apikey)
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
