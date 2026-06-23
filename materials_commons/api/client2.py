from .activity_mixin import ActivityMixin
from .client_base import ClientBase
from .community_mixin import CommunityMixin
from .dataset_mixin import DatasetMixin
from .directory_mixin import DirectoryMixin
from .entity_mixin import EntityMixin
from .experiment_mixin import ExperimentMixin
from .file_mixin import FileMixin
from .globus_mixin import GlobusMixin
from .mql_mixin import MQLMixin
from .project_mixin import ProjectMixin
from .published_dataset_mixin import PublishedDatasetMixin
from .server_mixin import ServerMixin
from .tag_mixin import TagMixin
from .user_mixin import UserMixin


class Client2(
    ServerMixin,
    ProjectMixin,
    ExperimentMixin,
    DirectoryMixin,
    FileMixin,
    EntityMixin,
    ActivityMixin,
    DatasetMixin,
    PublishedDatasetMixin,
    GlobusMixin,
    UserMixin,
    CommunityMixin,
    TagMixin,
    MQLMixin,
    ClientBase,
):
    """
    API client for the Materials Commons REST API using dataclass models.

    All methods return dataclass instances from models2.py, decoded via decoder.py.
    HTTP infrastructure (auth, rate limiting, throttling) is provided by ClientBase.

    FileMixin must precede ProjectMixin and PublishedDatasetMixin in the MRO because
    those mixins rely on FileMixin._get_files_matching being available on self.
    The inheritance order above satisfies this requirement.
    """
    pass
