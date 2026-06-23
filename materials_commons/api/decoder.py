from __future__ import annotations

from typing import Any, Callable, TypeVar

from .models2 import (
    Activity,
    Community,
    Dataset,
    Entity,
    Experiment,
    File,
    GlobusDownload,
    GlobusTransfer,
    GlobusUpload,
    Link,
    Paged,
    Project,
    Searchable,
    Server,
    Tag,
    User,
    Workflow,
)
from .util import get_date


T = TypeVar("T")


def decode_list(decoder: Callable[[dict[str, Any]], T], data) -> list[T]:
    if data is None:
        return []
    return [decoder(item) for item in data]


def decode_common_kwargs(data) -> dict[str, Any]:
    data = data or {}

    return {
        "id": data.get("id", None),
        "uuid": data.get("uuid", None),
        "name": data.get("name", None),
        "description": data.get("description", None),
        "summary": data.get("summary", None),
        "owner_id": data.get("owner_id", None),
        "owner": decode_user(data["owner"]) if data.get("owner", None) else None,
        "created_at": get_date("created_at", data),
        "updated_at": get_date("updated_at", data),
        "project_id": data.get("project_id", None),
    }


def decode_paged(paged, data=None) -> Paged:
    paged = paged or {}

    return Paged(
        current_page=paged.get("current_page", None),
        last_page=paged.get("last_page", None),
        per_page=paged.get("per_page", None),
        total=paged.get("total", None),
        data=data,
    )


def decode_community(data) -> Community:
    data = data or {}

    return Community(
        **decode_common_kwargs(data),
        public=data.get("public", None),
        files=decode_file_list_from_attr(data),
        links=decode_link_list_from_attr(data),
        datasets=decode_dataset_list_from_attr(data),
    )


def decode_community_list(data) -> list[Community]:
    return decode_list(decode_community, data)


def decode_community_list_from_attr(data, attr="communities") -> list[Community]:
    data = data or {}
    return decode_community_list(data.get(attr, []))


def decode_activity(data) -> Activity:
    data = data or {}

    return Activity(
        **decode_common_kwargs(data),
        entities=decode_entity_list_from_attr(data),
        files=decode_file_list_from_attr(data),
    )


def decode_activity_list(data) -> list[Activity]:
    return decode_list(decode_activity, data)


def decode_activity_list_from_attr(data, attr="activities") -> list[Activity]:
    data = data or {}
    return decode_activity_list(data.get(attr, []))


def decode_dataset(data) -> Dataset:
    data = data or {}

    root_dir = data.get("rootDir", None)

    return Dataset(
        **decode_common_kwargs(data),
        license=data.get("license", None),
        license_link=decode_license_link(data),
        doi=data.get("doi", None),
        authors=data.get("authors", None),
        file_selection=data.get("file_selection", None),
        zipfile_size=data.get("zipfile_size", None),
        zipfile_name=data.get("zipfile_name", None),
        workflows=decode_workflow_list_from_attr(data),
        experiments=decode_experiment_list_from_attr(data),
        activities=decode_activity_list_from_attr(data),
        entities=decode_entity_list_from_attr(data),
        files=decode_file_list_from_attr(data),
        globus_path=data.get("globus_path", None),
        globus_endpoint_id=data.get("globus_endpoint_id", None),
        experiments_count=data.get("experiments_count", None),
        files_count=data.get("files_count", None),
        workflows_count=data.get("workflows_count", None),
        activities_count=data.get("activities_count", None),
        entities_count=data.get("entities_count", None),
        comments_count=data.get("comments_count", None),
        published_at=get_date("published_at", data),
        tags=decode_tag_list_from_attr(data),
        root_dir=decode_file(root_dir) if root_dir else None,
    )


def decode_dataset_list(data) -> list[Dataset]:
    return decode_list(decode_dataset, data)


def decode_dataset_list_from_attr(data, attr="datasets") -> list[Dataset]:
    data = data or {}
    return decode_dataset_list(data.get(attr, []))


def decode_license_link(data) -> str | None:
    data = data or {}

    license_name = data.get("license", None)
    if not license_name:
        return None

    license_link = data.get("license_link", None)
    if license_link:
        return license_link

    if license_name == "Public Domain Dedication and License (PDDL)":
        return "https://opendatacommons.org/licenses/pddl/summary"
    if license_name == "Attribution License (ODC-By)":
        return "https://opendatacommons.org/licenses/by/summary"
    if license_name == "Open Database License (ODC-ODbL)":
        return "https://opendatacommons.org/licenses/odbl/summary"

    return "https://opendatacommons.org"


def decode_entity(data) -> Entity:
    data = data or {}

    return Entity(
        **decode_common_kwargs(data),
        activities=decode_activity_list_from_attr(data),
        files=decode_file_list_from_attr(data),
    )


def decode_entity_list(data) -> list[Entity]:
    return decode_list(decode_entity, data)


def decode_entity_list_from_attr(data, attr="entities") -> list[Entity]:
    data = data or {}
    return decode_entity_list(data.get(attr, []))


def decode_experiment(data) -> Experiment:
    data = data or {}

    return Experiment(
        **decode_common_kwargs(data),
        workflows=decode_workflow_list_from_attr(data),
        activities=decode_activity_list_from_attr(data),
        entities=decode_entity_list_from_attr(data),
        files=decode_file_list_from_attr(data),
    )


def decode_experiment_list(data) -> list[Experiment]:
    return decode_list(decode_experiment, data)


def decode_experiment_list_from_attr(data, attr="experiments") -> list[Experiment]:
    data = data or {}
    return decode_experiment_list(data.get(attr, []))


def decode_file(data) -> File:
    data = data or {}

    directory_data = data.get("directory", None)

    file = File(
        **decode_common_kwargs(data),
        mime_type=data.get("mime_type", None),
        path=data.get("path", None),
        directory_id=data.get("directory_id", None),
        size=data.get("size", None),
        checksum=data.get("checksum", None),
        experiments_count=data.get("experiments_count", None),
        activities_count=data.get("activities_count", None),
        entities_count=data.get("entities_count", None),
        entity_states_count=data.get("entity_states_count", None),
        previous_versions_count=data.get("previous_versions_count", None),
        directory=decode_file(directory_data) if directory_data else None,
    )

    if file.directory:
        file.make_path()

    return file


def decode_file_list(data) -> list[File]:
    return decode_list(decode_file, data)


def decode_file_list_from_attr(data, attr="files") -> list[File]:
    data = data or {}
    return decode_file_list(data.get(attr, []))


def decode_globus_upload(data) -> GlobusUpload:
    data = data or {}

    return GlobusUpload(
        **decode_common_kwargs(data),
        globus_endpoint_id=data.get("globus_endpoint_id", None),
        globus_url=data.get("globus_url", None),
        globus_path=data.get("globus_path", None),
        status=data.get("status", None),
    )


def decode_globus_upload_list(data) -> list[GlobusUpload]:
    return decode_list(decode_globus_upload, data)


def decode_globus_upload_list_from_attr(data, attr="globus_uploads") -> list[GlobusUpload]:
    data = data or {}
    return decode_globus_upload_list(data.get(attr, []))


def decode_globus_download(data) -> GlobusDownload:
    data = data or {}

    return GlobusDownload(
        **decode_common_kwargs(data),
        globus_endpoint_id=data.get("globus_endpoint_id", None),
        globus_url=data.get("globus_url", None),
        globus_path=data.get("globus_path", None),
        status=data.get("status", None),
    )


def decode_globus_download_list(data) -> list[GlobusDownload]:
    return decode_list(decode_globus_download, data)


def decode_globus_download_list_from_attr(data, attr="globus_uploads") -> list[GlobusDownload]:
    data = data or {}
    return decode_globus_download_list(data.get(attr, []))


def decode_globus_transfer(data) -> GlobusTransfer:
    data = data or {}

    return GlobusTransfer(
        id=data.get("id", None),
        uuid=data.get("uuid", None),
        globus_endpoint_id=data.get("globus_endpoint_id", None),
        globus_url=data.get("globus_url", None),
        globus_path=data.get("globus_path", None),
        state=data.get("state", None),
        last_globus_transfer_id_completed=data.get("last_globus_transfer_id_completed", None),
        latest_globus_transfer_completed_date=data.get("latest_globus_transfer_completed_date", None),
        project_id=data.get("project_id", None),
        owner_id=data.get("owner_id", None),
        transfer_request_id=data.get("transfer_request_id", None),
        created_at=get_date("created_at", data),
        updated_at=get_date("updated_at", data),
    )


def decode_globus_transfer_list(data) -> list[GlobusTransfer]:
    return decode_list(decode_globus_transfer, data)


def decode_globus_transfer_list_from_attr(data, attr="globus_transfers") -> list[GlobusTransfer]:
    data = data or {}
    return decode_globus_transfer_list(data.get(attr, []))


def decode_link(data) -> Link:
    data = data or {}

    return Link(
        **decode_common_kwargs(data),
        url=data.get("url", data),
    )


def decode_link_list(data) -> list[Link]:
    return decode_list(decode_link, data)


def decode_link_list_from_attr(data, attr="links") -> list[Link]:
    data = data or {}
    return decode_link_list(data.get(attr, []))


def decode_project(data) -> Project:
    data = data or {}

    root_dir = data.get("rootDir", None)

    return Project(
        **decode_common_kwargs(data),
        slug=data.get("slug", None),
        is_active=data.get("is_active", None),
        activities=decode_activity_list_from_attr(data),
        workflows=decode_workflow_list_from_attr(data),
        experiments=decode_experiment_list_from_attr(data),
        entities=decode_entity_list_from_attr(data),
        members=decode_user_list_from_attr(data, "members"),
        admins=decode_user_list_from_attr(data, "admins"),
        files={},
        client=None,
        root_dir=decode_file(root_dir) if root_dir else None,
    )


def decode_project_list(data) -> list[Project] | None:
    if data:
        return decode_list(decode_project, data)
    return None


def decode_project_list_from_attr(data, attr="projects") -> list[Project] | None:
    data = data or {}
    return decode_project_list(data.get(attr, []))


def decode_server(data) -> Server:
    data = data or {}

    return Server(
        globus_endpoint_id=data.get("globus_endpoint_id", None),
        institution=data.get("institution", None),
        version=data.get("version", None),
        last_updated_at=data.get("last_updated_at", data),
        first_deployed_at=data.get("first_deployed_at", data),
        contact=data.get("contact", None),
        description=data.get("description", None),
        name=data.get("name", None),
        uuid=data.get("uuid", None),
    )


def decode_tag(data) -> Tag:
    data = data or {}

    return Tag(
        id=data.get("id", None),
        name=data.get("name", None),
        slug=data.get("slug", None),
        created_at=get_date("created_at", data),
        updated_at=get_date("updated_at", data),
    )


def decode_tag_list(data) -> list[Tag]:
    return decode_list(decode_tag, data)


def decode_tag_list_from_attr(data, attr="tags") -> list[Tag]:
    data = data or {}
    return decode_tag_list(data.get(attr, []))


def decode_user(data) -> User:
    data = data or {}

    return User(
        id=data.get("id", None),
        uuid=data.get("uuid", None),
        name=data.get("name", None),
        email=data.get("email", None),
        description=data.get("description", None),
        affiliation=data.get("affiliation", None),
        slug=data.get("slug", None),
        created_at=get_date("created_at", data),
        updated_at=get_date("updated_at", data),
    )


def decode_user_list(data) -> list[User]:
    return decode_list(decode_user, data)


def decode_user_list_from_attr(data, attr="users") -> list[User]:
    data = data or {}
    return decode_user_list(data.get(attr, []))


def decode_searchable(data) -> Searchable:
    data = data or {}

    item = None
    searchable_data = data.get("searchable", None)

    if data.get("type") == "datasets" and searchable_data:
        item = decode_dataset(searchable_data)
    elif data.get("type") == "communities" and searchable_data:
        item = decode_community(searchable_data)

    return Searchable(
        title=data.get("title", None),
        url=data.get("url", None),
        type=data.get("type", None),
        item=item,
    )


def decode_searchable_list(data) -> list[Searchable]:
    return decode_list(decode_searchable, data)


def decode_workflow(data) -> Workflow:
    data = data or {}

    return Workflow(
        **decode_common_kwargs(data),
    )


def decode_workflow_list(data) -> list[Workflow]:
    return decode_list(decode_workflow, data)


def decode_workflow_list_from_attr(data, attr="workflows") -> list[Workflow]:
    data = data or {}
    return decode_workflow_list(data.get(attr, []))