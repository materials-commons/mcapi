import json


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
                 communities=None, tags=None, file1_id=None, file2_id=None, file3_id=None, file4_id=None,
                 file5_id=None):
        super(CreateDatasetRequest, self).__init__()

        self.description = description
        self.summary = summary
        self.license = license
        self.experiments = experiments
        self.communities = communities

        self.ds_authors = authors
        if self.ds_authors is not None:
            self.ds_authors = json.dumps(self.ds_authors)

        self.tags = tags
        if self.tags is not None:
            self.tags = json.dumps(self.tags)

        self.file1_id = file1_id
        self.file2_id = file2_id
        self.file3_id = file3_id
        self.file4_id = file4_id
        self.file5_id = file5_id


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
        self.category = "experimental"


# Activity Requests
class CreateActivityRequest(RequestCommon):
    def __init__(self, description=None, experiment_id=None):
        super(CreateActivityRequest, self).__init__()
        self.description = description
        self.experiment_id = experiment_id


# Community Requests
class CreateCommunityRequest(RequestCommon):
    def __init__(self, description=None, summary=None, public=False):
        super(CreateCommunityRequest, self).__init__()
        self.description = description
        self.summary = summary
        self.public = public


# Link Requests
class CreateLinkRequest(RequestCommon):
    def __init__(self, description=None, summary=None):
        super(CreateLinkRequest, self).__init__()
        self.description = description
        self.summary = summary
