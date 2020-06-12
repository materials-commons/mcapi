from .util import get_date


def from_list(cls, data):
    if data is None:
        return []
    return [cls(d) for d in data]


class Common(object):
    def __init__(self, data, has_project_id=True):
        self._data = data.copy()
        self.id = data.get('id', None)
        self.uuid = data.get('uuid', None)
        self.name = data.get('name', None)
        self.description = data.get('description', None)
        self.summary = data.get('summary', None)
        self.owner_id = data.get('owner_id', None)
        self.created_at = get_date('created_at', data)
        self.updated_at = get_date('updated_at', data)
        if has_project_id:
            self.project_id = data.get('project_id', None)


class Project(Common):
    def __init__(self, data={}):
        super(Project, self).__init__(data, has_project_id=False)
        self.is_active = data.get('is_active', None)
        self.activities = Activity.from_list_attr(data)
        self.workflows = Workflow.from_list_attr(data)
        self.experiments = Experiment.from_list_attr(data)
        self.activities = Activity.from_list_attr(data)
        self.entities = Entity.from_list_attr(data)

    @staticmethod
    def from_list(data):
        return from_list(Project, data)

    @staticmethod
    def from_list_attr(data, attr='projects'):
        return Project.from_list(data.get(attr, []))


class Activity(Common):
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
    def __init__(self, data={}):
        super(Dataset, self).__init__(data)
        self.workflows = Workflow.from_list_attr(data)
        self.experiments = Experiment.from_list_attr(data)
        self.activities = Activity.from_list_attr(data)
        self.entities = Entity.from_list_attr(data)
        self.files = File.from_list_attr(data)

    @staticmethod
    def from_list(data):
        return from_list(Dataset, data)

    @staticmethod
    def from_list_attr(data, attr='datasets'):
        return Dataset.from_list(data.get(attr, []))


class Entity(Common):
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
    def __init__(self, data={}):
        super(File, self).__init__(data)
        self.mime_type = data.get('mime_type', None)
        self.path = data.get('path', None)
        self.directory_id = data.get('directory_id', None)
        self.size = data.get('size', None)
        self.checksum = data.get('checksum', None)

    @staticmethod
    def from_list(data):
        return from_list(File, data)

    @staticmethod
    def from_list_attr(data, attr='files'):
        return File.from_list(data.get(attr, []))


class User(object):
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

    @staticmethod
    def from_list(data):
        return from_list(User, data)

    @staticmethod
    def from_list_attr(data, attr='users'):
        return User.from_list(data.get(attr, []))


class Workflow(Common):
    def __init__(self, data={}):
        super(Workflow, self).__init__(data)

    @staticmethod
    def from_list(data):
        return from_list(Workflow, data)

    @staticmethod
    def from_list_attr(data, attr='workflows'):
        return Workflow.from_list(data.get(attr, []))


class GlobusUpload(Common):
    def __init__(self, data={}):
        super(GlobusUpload, self).__init__(data)
        self.globus_endpoint_id = data.get('globus_endpoint_id', None)
        self.globus_url = data.get('globus_url', None)
        self.globus_path = data.get('globus_path', None)

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
