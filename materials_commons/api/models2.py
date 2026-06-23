from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Paged:
    current_page: int | None = None
    last_page: int | None = None
    per_page: int | None = None
    total: int | None = None
    data: Any = None


@dataclass
class Common:
    """
    Base class for most models. Contains common attributes shared across most model objects.
    """

    id: int | None = None
    uuid: str | None = None
    name: str | None = None
    description: str | None = None
    summary: str | None = None
    owner_id: int | None = None
    owner: User | None = None
    created_at: str | None = None
    updated_at: str | None = None
    project_id: int | None = None


@dataclass
class Community(Common):
    """
    Community represents a Materials Commons Community of Practice.
    """

    public: bool | None = None
    files: list[File] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)
    datasets: list[Dataset] = field(default_factory=list)


@dataclass
class Activity(Common):
    """
    An activity represents a step that operates on one or more Entities.
    """

    entities: list[Entity] = field(default_factory=list)
    files: list[File] = field(default_factory=list)


@dataclass
class Dataset(Common):
    """
    A dataset represents a collection of files, activities and entities, along with other metadata.
    """

    license: str | None = None
    license_link: str | None = None
    doi: str | None = None
    authors: str | None = None
    file_selection: dict[str, Any] | None = None
    zipfile_size: int | None = None
    zipfile_name: str | None = None
    workflows: list[Workflow] = field(default_factory=list)
    experiments: list[Experiment] = field(default_factory=list)
    activities: list[Activity] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    files: list[File] = field(default_factory=list)
    globus_path: str | None = None
    globus_endpoint_id: str | None = None
    experiments_count: int | None = None
    files_count: int | None = None
    workflows_count: int | None = None
    activities_count: int | None = None
    entities_count: int | None = None
    comments_count: int | None = None
    published_at: str | None = None
    tags: list[Tag] = field(default_factory=list)
    root_dir: File | None = None


@dataclass
class Entity(Common):
    """
    An entity represents a virtual or physical specimen, sample, or object.
    """

    activities: list[Activity] = field(default_factory=list)
    files: list[File] = field(default_factory=list)


@dataclass
class Experiment(Common):
    """
    An experiment is a container for entities, activities, and files.
    """

    workflows: list[Workflow] = field(default_factory=list)
    activities: list[Activity] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    files: list[File] = field(default_factory=list)


@dataclass
class File(Common):
    """
    A file is an uploaded file associated with a project in Materials Commons.
    """

    mime_type: str | None = None
    path: str | None = None
    directory_id: int | None = None
    size: int | None = None
    checksum: str | None = None
    experiments_count: int | None = None
    activities_count: int | None = None
    entities_count: int | None = None
    entity_states_count: int | None = None
    previous_versions_count: int | None = None
    directory: File | None = None

    def make_path(self):
        if self.directory is None:
            return

        if self.directory.path == "/":
            self.path = self.directory.path + self.name
        else:
            self.path = self.directory.path + "/" + self.name


@dataclass
class GlobusUpload(Common):
    globus_endpoint_id: str | None = None
    globus_url: str | None = None
    globus_path: str | None = None
    status: str | None = None


@dataclass
class GlobusDownload(Common):
    globus_endpoint_id: str | None = None
    globus_url: str | None = None
    globus_path: str | None = None
    status: str | None = None


@dataclass
class GlobusTransfer:
    """
    A GlobusTransfer represents a started Globus transfer, whether it is an upload or a download.
    """

    id: int | None = None
    uuid: str | None = None
    globus_endpoint_id: str | None = None
    globus_url: str | None = None
    globus_path: str | None = None
    state: str | None = None
    last_globus_transfer_id_completed: str | None = None
    latest_globus_transfer_completed_date: str | None = None
    project_id: int | None = None
    owner_id: int | None = None
    transfer_request_id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class Link(Common):
    """
    A Link represents a URL.
    """

    url: str | None = None


@dataclass
class Project(Common):
    """
    A project is the top-level object that stores files and metadata about a research project.
    """

    slug: str | None = None
    is_active: bool | None = None
    activities: list[Activity] = field(default_factory=list)
    workflows: list[Workflow] = field(default_factory=list)
    experiments: list[Experiment] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    members: list[User] = field(default_factory=list)
    admins: list[User] = field(default_factory=list)
    files: dict[str, Path] = field(default_factory=dict)
    client: Any = None
    root_dir: File | None = None

    def get_file(self, path):
        if self.client is None:
            raise Exception("client not set")
        if path not in self.files:
            self._download_file(path)
        return self.files[path]

    def _download_file(self, path):
        download_dir = Path.home().joinpath(".materialscommons", "file_cache", self.uuid)
        path_dir = os.path.dirname(path)
        file_dir = Path(download_dir).joinpath(path_dir[1:len(path_dir)])
        os.makedirs(file_dir, exist_ok=True)
        download_to = Path(download_dir).joinpath(path[1:len(path)])
        self.client.download_file_by_path(self.id, path, str(download_to))
        self.files[path] = download_to

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client is not None and self.files is not None:
            dir_to_delete = Path.home().joinpath(".materialscommons", "file_cache", self.uuid)
            try:
                shutil.rmtree(dir_to_delete)
            finally:
                pass


@dataclass
class Server:
    """
    A Server contains information about the Materials Commons server hosting the API.
    """

    globus_endpoint_id: str | None = None
    institution: str | None = None
    version: str | None = None
    last_updated_at: str | None = None
    first_deployed_at: str | None = None
    contact: str | None = None
    description: str | None = None
    name: str | None = None
    uuid: str | None = None


@dataclass
class Tag:
    """
    A tag is an attribute that can be added to different objects in the system.
    """

    id: int | None = None
    name: str | None = None
    slug: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class User:
    """
    A User represents a user account on Materials Commons.
    """

    id: int | None = None
    uuid: str | None = None
    name: str | None = None
    email: str | None = None
    description: str | None = None
    affiliation: str | None = None
    slug: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class Searchable:
    """
    A Searchable represents the results of a search.
    """

    title: str | None = None
    url: str | None = None
    type: str | None = None
    item: Dataset | Community | None = None


@dataclass
class Workflow(Common):
    """
    A workflow is a graphical and textual representation a user created for an experimental workflow.
    """