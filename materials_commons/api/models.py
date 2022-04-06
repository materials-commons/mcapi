from .util import get_date


def from_list(cls, data):
    if data is None:
        return []
    return [cls(d) for d in data]


def pretty_print(clas, indent=0):
    """
    Prints to stdout a formatted version of the object. This will recursively print sub-objects as well as iterate
    over lists of objects maintaining proper indenting. Private attributes are ignored.
    """
    print(' ' * indent + type(clas).__name__ + ':')
    indent += 4
    for k, v in clas.__dict__.items():
        if '__dict__' in dir(v):
            pretty_print(v, indent)
        elif isinstance(v, list):
            print(' ' * indent + k + ': ')
            for item in v:
                pretty_print(item, indent + 4)
        else:
            if k != '_data':
                print(' ' * indent + k + ': ' + str(v))


class Common(object):
    """
    Base class for most models. Contains common attributes shared across most model objects.

    Attributes
    ----------
    id : int
        The id of the object.
    uuid : str
        The uuid of the object.
    name : str
        Name of model object.
    description : str
        Description of the model instance, for example a description of a project.
    summary : str
        A short description suitable for display in a table.
    owner_id : int
        The id of the owner of the model instance.
    owner : mcapi.Owner
        The full owner model associated with the owner_id.
    created_at : str
        Formatted string datetime when the object was created. String format is "%Y-%m-%dT%H:%M:%S.%fZ".
    updated_at : str
        Formatted string datetime when the object was last updated. String format is "%Y-%m-%dT%H:%M:%S.%fZ".
    project_id : int
        The project_id is an optional field that exists only if the underlying model has a project_id field. The
        project_id is the id of the project the object is associated with.

    Methods
    -------
    pretty_print()
        Prints to stdout a formatted version of the object. This will recursively print sub-objects as well as iterate
        over lists of objects maintaining proper indenting. Private attributes are ignored.
    """
    def __init__(self, data):
        self._data = data.copy()
        self.id = data.get('id', None)
        self.uuid = data.get('uuid', None)
        self.name = data.get('name', None)
        self.description = data.get('description', None)
        self.summary = data.get('summary', None)
        self.owner_id = data.get('owner_id', None)
        self.created_at = get_date('created_at', data)
        self.updated_at = get_date('updated_at', data)
        project_id = data.get('project_id', None)
        if project_id:
            self.project_id = project_id
        owner = data.get('owner', None)
        if owner:
            self.owner = User(owner)

    def pretty_print(self):
        pretty_print(self)


class Community(Common):
    """
    Community represents a Materials Commons Community of Practice. A Community of Practice is place to gather
    similar published datasets together. In addition it contains links and files that are specific to a community. For
    example it may contain a link to a forum associated with the community, or a file with suggested naming conventions.

    Attributes:
    -----------
    public : bool
        A flag that is true if this community is public and viewable by anyone.
    files : list of mcapi.File
        Files associated with the community.
    links: list of mcapi.Link
        Links associated with the community.
    datasets: list of mcapi.Dataset
        List of published datasets associated with the community.
    """
    def __init__(self, data={}):
        super(Community, self).__init__(data)
        self.public = data.get('public', None)
        self.files = File.from_list_attr(data)
        self.links = Link.from_list_attr(data)
        self.datasets = Dataset.from_list_attr(data)

    @staticmethod
    def from_list(data):
        return from_list(Community, data)

    @staticmethod
    def from_list_attr(data, attr='communities'):
        return Community.from_list(data.get(attr, []))


class Activity(Common):
    """
    An activity represents a step that operates on one or more Entities. For example an Entity maybe have been heat
    treated. In that case an Activity representing the heat treatment step could be associated with the Entity. An
    activity may also have files associated with it. These may represent files produced by that activity. For example
    the images produced from running an SEM. All the files from the SEM will be associated with the activity. A subset
    of these files may be represented with an Entity that the SEM operated on.

    Attributes:
    ----------
    entities: list of mcapi.Entity
        The list of entities associated with this activity.
    files: list of mcapi.File
        The list of files associated with this activity.
    """
    def __init__(self, data={}):
        super(Activity, self).__init__(data)
        self.entities = Entity.from_list_attr(data)
        self.files = File.from_list_attr(data)

    @staticmethod
    def from_list(data):
        return from_list(Activity, data)

    @staticmethod
    def from_list_attr(data, attr='activities'):
        return Activity.from_list(data.get(attr, []))


class Dataset(Common):
    """
    A dataset represents a collection of files, activities and entities, along with other meta data such as authors,
    papers, etc... that is meant to be shared as a whole. A dataset can be published, in which case the dataset is
    available to the public, and its associated files can be downloaded.

    Attributes:
    -----------
    license : str
        The license (if any) associated with the dataset.
    license_url : str
        The url of the license associated with the dataset. Currently licenses all come from Open Data Commons.
    doi : str
        The DOI associated with the dataset.
    authors : str
        A semi-colon separated string of the authors for the dataset.
    file_selection : dict
        The file_selection is a selection of files and directories to include/exclude in a dataset when it is published.
        The file_selection has the following fields (each field is a list): include_files, exclude_files, include_dirs,
        exclude_dirs.
    zipfile_size : int
        If a zipfile was built for this dataset then this is the size of the zipfile in bytes.
    zipfile_name : str
        If a zipfile was build for this dataset then this is the name of the zipfile.
    workflows : list of mcapi.Workflow
        The list of workflows associated with the dataset.
    experiments : list of mcapi.Experiment
        The list of experiments associated with the dataset.
    activities: list of mcapi.Activity
        The list of activities included with the dataset.
    entities: list of mcapi.Entity
        The list of entities included with the dataset.
    files : list of mcapi.File
        The list of files included with the dataset.
    globus_path : str
        The globus path for using globus to access the dataset files.
    globus_endpoint_id : str
        The globus endpoint the dataset files are stored on.
    workflows_count : int
        Count of workflows included with dataset.
    activities_count : int
        Count of activities included with dataset.
    entities_count : int
        Count of entities included with dataset.
    comments_count : int
        Count of comments associated with dataset.
    published_at : str
        The date the dataset was published on.
    tags : list of mcapi.Tag
        The tags associated with the dataset.
    root_dir : mcapi.File
        The root directory (/) for published datasets. Unpublished datasets do not have a root directory.
    """
    def __init__(self, data={}):
        super(Dataset, self).__init__(data)
        self.license = data.get('license', None)
        self.license_link = self._get_license_link(data)
        self.doi = data.get('doi', None)
        self.authors = data.get('authors', None)
        self.file_selection = data.get('file_selection', None)
        self.zipfile_size = data.get('zipfile_size', None)
        self.zipfile_name = data.get('zipfile_name', None)
        self.workflows = Workflow.from_list_attr(data)
        self.experiments = Experiment.from_list_attr(data)
        self.activities = Activity.from_list_attr(data)
        self.entities = Entity.from_list_attr(data)
        self.files = File.from_list_attr(data)
        self.globus_path = data.get('globus_path', None)
        self.globus_endpoint_id = data.get('globus_endpoint_id', None)
        self.experiments_count = data.get('experiments_count', None)
        self.files_count = data.get('files_count', None)
        self.workflows_count = data.get('workflows_count', None)
        self.activities_count = data.get('activities_count', None)
        self.entities_count = data.get('entities_count', None)
        self.comments_count = data.get('comments_count', None)
        self.published_at = get_date('published_at', data)
        self.tags = Tag.from_list_attr(data)
        root_dir = data.get('rootDir', None)
        if root_dir:
            self.root_dir = File(root_dir)

    def _get_license_link(self, data):
        if not self.license:
            return None

        license_link = data.get('license_link', None)
        if license_link:
            return license_link
        if self.license == "Public Domain Dedication and License (PDDL)":
            return "https://opendatacommons.org/licenses/pddl/summary"
        elif self.license == "Attribution License (ODC-By)":
            return "https://opendatacommons.org/licenses/by/summary"
        elif self.license == "Open Database License (ODC-ODbL)":
            return "https://opendatacommons.org/licenses/odbl/summary"
        else:
            return "https://opendatacommons.org"

    @staticmethod
    def from_list(data):
        return from_list(Dataset, data)

    @staticmethod
    def from_list_attr(data, attr='datasets'):
        return Dataset.from_list(data.get(attr, []))


class Entity(Common):
    """
    An entity represent a virtual or physical specimen, sample or object. An entity is what is being measured or
    transformed. An example of an entity would be a sheet of metal that is be tested. That sheet might be heated
    (Activity), cut (Activity) then viewed on a SEM (Activity).

    Attributes:
    ----------
    activities: list of mcapi.Activity
        The list of activities associated with this entity.
    files: list of mcapi.File
        The list of files associated with this entity.
    """
    def __init__(self, data={}):
        super(Entity, self).__init__(data)
        self.activities = Activity.from_list_attr(data)
        self.files = File.from_list_attr(data)

    @staticmethod
    def from_list(data):
        return from_list(Entity, data)

    @staticmethod
    def from_list_attr(data, attr='entities'):
        return Entity.from_list(data.get(attr, []))


class Experiment(Common):
    """
    An experiment is a container for entities, activities, and files.

    Attributes:
    -----------
    workflows : list of mcapi.Workflow
        The list of workflows used in the experiment.
    activities : list of mcapi.Activity
        The list of activities used in the experiment.
    entities : list of mcapi.Entity
        The list of entities used in the experiment.
    files : list of mcapi.File
        The list of files used in the experiment.
    """
    def __init__(self, data={}):
        super(Experiment, self).__init__(data)
        self.workflows = Workflow.from_list_attr(data)
        self.activities = Activity.from_list_attr(data)
        self.entities = Entity.from_list_attr(data)
        self.files = File.from_list_attr(data)

    @staticmethod
    def from_list(data):
        return from_list(Experiment, data)

    @staticmethod
    def from_list_attr(data, attr='experiments'):
        return Experiment.from_list(data.get(attr, []))


class File(Common):
    """
    A file is an uploaded file associated with a project in Materials Commons.

    Attributes:
    -----------
    mime_type : str
        The mime_type. If File is a directory then mime_type will be set to 'directory'.
    path : str
        The path. This is set for directories and derived for files by checking if the directory
        is included, and if so updating the file path to be the directory path + the file name.
    directory_id : int
        The id of the directory the file is in.
    size : int
        The size of the file. Set to zero for directories.
    checksum : str
        The checksum of the file. None for directories.
    experiments_count : int
        The number of experiments the file is in. None if file is for a published dataset or a directory.
    activities_count : int
        The number of activities that include the file. None if a directory.
    entities_count : int
        The number of entities that include the file. None if a directory.
    entity_states_count : int
        The number of entity states that include the file. None if a directory.
    previous_versions_count : int
        Number of previous file versions. None if a directory.
    directory : mcapi.File
        The directory object for the file. If the file is the root directory then this will be set to None.
    """
    def __init__(self, data={}):
        super(File, self).__init__(data)
        self.mime_type = data.get('mime_type', None)
        self.path = data.get('path', None)
        self.directory_id = data.get('directory_id', None)
        self.size = data.get('size', None)
        self.checksum = data.get('checksum', None)
        self.experiments_count = data.get('experiments_count', None)
        self.activities_count = data.get('activities_count', None)
        self.entities_count = data.get('entities_count', None)
        self.entity_states_count = data.get('entity_states_count', None)
        self.previous_versions_count = data.get('previous_versions_count', None)
        directory = data.get('directory', None)
        if directory:
            self.directory = File(directory)
            self._make_path()
        else:
            self.directory = None

    def _make_path(self):
        if self.directory.path == "/":
            self.path = self.directory.path + self.name
        else:
            self.path = self.directory.path + "/" + self.name

    @staticmethod
    def from_list(data):
        return from_list(File, data)

    @staticmethod
    def from_list_attr(data, attr='files'):
        return File.from_list(data.get(attr, []))


class GlobusUpload(Common):
    def __init__(self, data={}):
        super(GlobusUpload, self).__init__(data)
        self.globus_endpoint_id = data.get('globus_endpoint_id', None)
        self.globus_url = data.get('globus_url', None)
        self.globus_path = data.get('globus_path', None)
        self.status = data.get('status', None)

    @staticmethod
    def from_list(data):
        return from_list(GlobusUpload, data)

    @staticmethod
    def from_list_attr(data, attr="globus_uploads"):
        return GlobusUpload.from_list(data.get(attr, []))


class GlobusDownload(Common):
    def __init__(self, data={}):
        super(GlobusDownload, self).__init__(data)
        self.globus_endpoint_id = data.get('globus_endpoint_id', None)
        self.globus_url = data.get('globus_url', None)
        self.globus_path = data.get('globus_path', None)
        self.status = data.get('status', None)

    @staticmethod
    def from_list(data):
        return from_list(GlobusDownload, data)

    @staticmethod
    def from_list_attr(data, attr="globus_uploads"):
        return GlobusDownload.from_list(data.get(attr, []))


class GlobusTransfer(object):
    """
    A GlobusTransfer represents a started globus transfer, whether its an upload or a download.

    Attributes:
    -----------
    id : int
        The id of the object.
    uuid : str
        The uuid of the object.
    globus_endpoint_id : str
        The globus endpoint id.
    globus_url : str
        The url for the globus endpoint.
    globus_path : str
        The globus path.
    state : str
        The state of the connection. One of 'open' (in use) or 'closed' (being cleaned up).
    last_globus_transfer_id_completed : str
        Currently not used.
    latest_globus_transfer_completed_date : str
        Currently not used.
    project_id : int
        The id of the project this transfer is associated with.
    owner_id : int
        The id of the user who started the transfer.
    transfer_request_id : id
        The id of the transfer request associated with this globus transfer.
    created_at : str
        Formatted string datetime when the object was created. String format is "%Y-%m-%dT%H:%M:%S.%fZ".
    updated_at : str
        Formatted string datetime when the object was last updated. String format is "%Y-%m-%dT%H:%M:%S.%fZ".
    """
    def __init__(self, data={}):
        self._data = data.copy()
        self.id = data.get('id', None)
        self.uuid = data.get('uuid', None)
        self.globus_endpoint_id = data.get('globus_endpoint_id', None)
        self.globus_url = data.get('globus_url', None)
        self.globus_path = data.get('globus_path', None)
        self.state = data.get('state', None)
        self.last_globus_transfer_id_completed = data.get('last_globus_transfer_id_completed', None)
        self.latest_globus_transfer_completed_date = data.get('latest_globus_transfer_completed_date', None)
        self.project_id = data.get('project_id', None)
        self.owner_id = data.get('owner_id', None)
        self.transfer_request_id = data.get('transfer_request_id', None)
        self.created_at = get_date('created_at', data)
        self.updated_at = get_date('updated_at', data)

    def pretty_print(self):
        pretty_print(self)

    @staticmethod
    def from_list(data):
        return from_list(GlobusTransfer, data)

    @staticmethod
    def from_list_attr(data, attr='globus_transfers'):
        return GlobusTransfer.from_list(data.get(attr, []))


class Link(Common):
    """
    A Link represents a URL.

    Attributes:
    -----------
    url : str
        The url for the link.
    """
    def __init__(self, data={}):
        super(Link, self).__init__(data)
        self.url = data.get('url', data)

    @staticmethod
    def from_list(data):
        return from_list(Link, data)

    @staticmethod
    def from_list_attr(data, attr='links'):
        return Link.from_list(data.get(attr, []))


class Project(Common):
    """
    A project is the top level object that stores files and meta data about your research project.

    Attributes:
    -----------
    workflows : list of mcapi.Workflow
        Workflows in the project.
    experiments : list of mcapi.Experiment
        Experiments in the project.
    activities : list of mcapi.Activity
        Activities in the project.
    entities : list of mcapi.Entity
        Entities in the project.
    members : list of mcapi.User
        Project members.
    admins : list of mcapi.User
        Project administrators
    root_dir : mcapi.File
        The root directory (/) of the project.
    """

    def __init__(self, data={}):
        super(Project, self).__init__(data)
        self.is_active = data.get('is_active', None)
        self.activities = Activity.from_list_attr(data)
        self.workflows = Workflow.from_list_attr(data)
        self.experiments = Experiment.from_list_attr(data)
        self.activities = Activity.from_list_attr(data)
        self.entities = Entity.from_list_attr(data)
        self.members = User.from_list_attr(data, 'members')
        self.admins = User.from_list_attr(data, 'admins')
        self.root_dir = None
        root_dir = data.get('rootDir', None)
        if root_dir:
            self.root_dir = File(root_dir)

    @staticmethod
    def from_list(data):
        return from_list(Project, data)

    @staticmethod
    def from_list_attr(data, attr='projects'):
        return Project.from_list(data.get(attr, []))


class Server(object):
    """
    A Server contains information about the Materials Commons server hosting the API.

    Attributes:
    -----------
    globus_endpoint_id : str
        The globus endpoint id for the server.
    institution : str
        The institution running this server instance.
    version : str
        Current version of the site.
    last_updated_at : str
        The date the server was last updated.
    first_deployed_at : str
        The date the server was first deployed.
    contact : str
        Contact email for the server.
    description : str
        A description of the server.
    name : str
        The name for this server instance.
    uuid : str
        A UUID that global identifies this server instance.
    """

    def __init__(self, data={}):
        self._data = data.copy()
        self.globus_endpoint_id = data.get('globus_endpoint_id', None)
        self.institution = data.get('institution', None)
        self.version = data.get('version', None)
        self.last_updated_at = data.get('last_updated_at', data)
        self.first_deployed_at = data.get('first_deployed_at', data)
        self.contact = data.get('contact', None)
        self.description = data.get('description', None)
        self.name = data.get('name', None)
        self.uuid = data.get('uuid', None)

    def pretty_print(self):
        pretty_print(self)


class Tag(object):
    """
    A tag is an attribute that can be added to different objects in the system. Currently only datasets support tags.

    Attributes:
    -----------
    id : int
        The id of the tag object.
    name : str
        The name of the tag.
    slug : str
        The name as a slug.
    created_at : str
        Formatted string datetime when the object was created. String format is "%Y-%m-%dT%H:%M:%S.%fZ".
    updated_at : str
        Formatted string datetime when the object was last updated. String format is "%Y-%m-%dT%H:%M:%S.%fZ".
    """

    def __init__(self, data={}):
        self._data = data.copy()
        self.id = data.get('id', None)
        self.name = data.get('name', None)
        self.slug = data.get('slug', None)
        self.created_at = get_date('created_at', data)
        self.updated_at = get_date('updated_at', data)

    def pretty_print(self):
        pretty_print(self)

    @staticmethod
    def from_list(data):
        return from_list(Tag, data)

    @staticmethod
    def from_list_attr(data, attr='tags'):
        return Tag.from_list(data.get(attr, []))


class User(object):
    """
    A User represents a user account on Materials Commons.

    Attributes:
    -----------
    id : int
        The id of the object.
    uuid : str
        The uuid of the object.
    name : str
        The users name.
    email : str
        The users email address.
    description : str
        The description the user entered about themselves.
    affiliation : str
        The affiliation the user entered.
    created_at : str
        Formatted string datetime when the object was created. String format is "%Y-%m-%dT%H:%M:%S.%fZ".
    updated_at : str
        Formatted string datetime when the object was last updated. String format is "%Y-%m-%dT%H:%M:%S.%fZ".
    """

    def __init__(self, data={}):
        self._data = data.copy()
        self.id = data.get('id', None)
        self.uuid = data.get('uuid', None)
        self.name = data.get('name', None)
        self.email = data.get('email', None)
        self.description = data.get('description', None)
        self.affiliation = data.get('affiliation', None)
        self.created_at = get_date('created_at', data)
        self.updated_at = get_date('updated_at', data)

    def pretty_print(self):
        pretty_print(self)

    @staticmethod
    def from_list(data):
        return from_list(User, data)

    @staticmethod
    def from_list_attr(data, attr='users'):
        return User.from_list(data.get(attr, []))


class Searchable(object):
    """
    A searchable represents the results of a search.

    Attributes:
    -----------
    title : str
        The title of the object (often the name).
    url : str
        The url of the object.
    type : str
        The type of the object as a string - "datasets" || "communities"
    item : mcapi.Dataset or mcapi.Community
        Depending on what type field is set to the item will be one of the above types.
    """

    def __init__(self, data={}):
        self._data = data.copy()
        self.title = data.get('title')
        self.url = data.get('url')
        self.type = data.get('type')
        self._fill_item()

    def pretty_print(self):
        pretty_print(self)

    def _fill_item(self):
        if self.type == "datasets":
            self.item = Dataset(self._data["searchable"])
        elif self.type == "communities":
            self.item = Community(self._data["searchable"])

    @staticmethod
    def from_list(data):
        return from_list(Searchable, data)


class Workflow(Common):
    """
    A workflow is a graphical and textual representation a user created for an experimental workflow.
    """
    def __init__(self, data={}):
        super(Workflow, self).__init__(data)

    @staticmethod
    def from_list(data):
        return from_list(Workflow, data)

    @staticmethod
    def from_list_attr(data, attr='workflows'):
        return Workflow.from_list(data.get(attr, []))
