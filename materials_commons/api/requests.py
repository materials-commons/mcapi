class RequestCommon(object):
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


# Project Requests
class CreateProjectRequest(RequestCommon):
    def __init__(self, description=None, summary=None):
        super(CreateProjectRequest, self).__init__()
        self.description = description
        self.summary = summary
        self.is_active = True


class UpdateProjectRequest(RequestCommon):
    def __init__(self, name, description=None, summary=None):
        super(UpdateProjectRequest, self).__init__()
        self.description = description
        self.summary = summary
        self.name = name


# Dataset Requests
class CreateDatasetRequest(RequestCommon):
    def __init__(self, description=None, summary=None, license=None, authors=None, experiments=None,
                 communities=None, tags=None):
        super(CreateDatasetRequest, self).__init__()
        self.description = description
        self.summary = summary
        self.license = license
        self.authors = authors
        self.experiments = experiments
        self.communities = communities
        self.tags = tags


class UpdateDatasetRequest(RequestCommon):
    def __init__(self, description=None, summary=None, license=None, authors=None, experiments=None,
                 communities=None, tags=None):
        super(UpdateDatasetRequest, self).__init__()
        self.description = description
        self.summary = summary
        self.license = license
        self.authors = authors
        self.experiments = experiments
        self.communities = communities
        self.tags = tags


# Experiment Requests
class CreateExperimentRequest(RequestCommon):
    def __init__(self, description=None, summary=None):
        super(CreateExperimentRequest, self).__init__()
        self.description = description
        self.summary = summary


class UpdateExperimentRequest(RequestCommon):
    def __init__(self, name=None, description=None, summary=None):
        super(UpdateExperimentRequest, self).__init__()
        self.name = name
        self.description = description
        self.summary = summary


# Directory Requests
class CreateDirectoryRequest(RequestCommon):
    def __init__(self, description=None):
        super(CreateDirectoryRequest, self).__init__()
        self.description = description


class UpdateDirectoryRequest(RequestCommon):
    def __init__(self, description=None):
        super(UpdateDirectoryRequest, self).__init__()
        self.description = description


# File Requests
class UpdateFileRequest(RequestCommon):
    def __init__(self, description=None, summary=None):
        super(UpdateFileRequest, self).__init__()
        self.description = description
        self.summary = summary


# Entity Requests
class CreateEntityRequest(RequestCommon):
    def __init__(self, description=None, summary=None, experiment_id=None):
        super(CreateEntityRequest, self).__init__()
        self.description = description
        self.summary = summary
        self.experiment_id = experiment_id


# Activity Requests
class CreateActivityRequest(RequestCommon):
    def __init__(self, description=None, experiment_id=None):
        super(CreateActivityRequest, self).__init__()
        self.description = description
        self.experiment_id = experiment_id
