import io
import os
import tempfile
from datetime import datetime

import pytest

from materials_commons.api.client import Client
from materials_commons.api.requests import (
    CreateActivityRequest,
    CreateCommunityRequest,
    CreateDatasetRequest,
    CreateDirectoryRequest,
    CreateEntityRequest,
    CreateExperimentRequest,
    CreateLinkRequest,
    CreateProjectRequest,
    UpdateDatasetRequest,
    UpdateDirectoryRequest,
    UpdateExperimentRequest,
    UpdateFileRequest,
    UpdateProjectRequest,
)


# =============================================================================
# Environment configuration
# =============================================================================
#
# Required:
#   MC_API_KEY
#
# Optional:
#   MC_BASE_URL
#   MC_RUN_MUTATING_TESTS=true
#
# Fill in relevant IDs/values in your shell environment:
#
#   export MC_PROJECT_ID="..."
#   export MC_USER_ID="..."
#   export MC_EXPERIMENT_ID="..."
#   export MC_WORKFLOW_ID="..."
#   export MC_DIRECTORY_ID="..."
#   export MC_PARENT_DIRECTORY_ID="..."
#   export MC_FILE_ID="..."
#   export MC_FILE_PATH="/path/in/project/file.txt"
#   export MC_DEST_DIRECTORY_ID="..."
#   export MC_ACTIVITY_ID="..."
#   export MC_ENTITY_ID="..."
#   export MC_DATASET_ID="..."
#   export MC_PUBLISHED_DATASET_ID="..."
#   export MC_PUBLISHED_DIRECTORY_ID="..."
#   export MC_PUBLISHED_FILE_ID="..."
#   export MC_GLOBUS_UPLOAD_ID="..."
#   export MC_GLOBUS_DOWNLOAD_ID="..."
#   export MC_USER_EMAIL="user@example.com"
#   export MC_COMMUNITY_ID="..."
#   export MC_COMMUNITY_FILE_ID="..."
#   export MC_COMMUNITY_LINK_ID="..."
#   export MC_AUTHOR="..."
#   export MC_TAG="..."
#   export MC_SEARCH="..."
#   export MC_UPLOAD_FILE_PATH="/local/path/to/upload.txt"
#
# Login/API-key tests also require:
#   export MC_LOGIN_EMAIL="..."
#   export MC_LOGIN_PASSWORD="..."
#
# =============================================================================


def env(name, default=None):
    return os.getenv(name, default)


def env_required(name):
    value = os.getenv(name)
    if not value:
        pytest.skip(f"Set {name} to run this test")
    return value


def env_int(name):
    return int(env_required(name))


def mutating_enabled():
    return env("MC_RUN_MUTATING_TESTS", "false").lower() == "true"


def skip_unless_mutating():
    if not mutating_enabled():
        pytest.skip("Set MC_RUN_MUTATING_TESTS=true to run mutating/destructive tests")


@pytest.fixture(scope="session")
def client():
    return Client(
        apikey=env_required("MC_API_KEY"),
        base_url=env("MC_BASE_URL", "https://materialscommons.org/api"),
    )


@pytest.fixture()
def temp_upload_file():
    with tempfile.NamedTemporaryFile("w+b", delete=False) as f:
        f.write(b"materials commons test file\n")
        path = f.name

    try:
        yield path
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


# =============================================================================
# Static methods / debug helpers
# =============================================================================


def test_get_apikey():
    email = env_required("MC_LOGIN_EMAIL")
    password = env_required("MC_LOGIN_PASSWORD")
    base_url = env("MC_BASE_URL", "https://materialscommons.org/api")

    api_key = Client.get_apikey(email, password, base_url)

    assert api_key


def test_login():
    email = env_required("MC_LOGIN_EMAIL")
    password = env_required("MC_LOGIN_PASSWORD")
    base_url = env("MC_BASE_URL", "https://materialscommons.org/api")

    logged_in_client = Client.login(email, password, base_url)

    assert isinstance(logged_in_client, Client)
    assert logged_in_client.apikey


def test_set_debug_on():
    Client.set_debug_on()


def test_set_debug_off():
    Client.set_debug_off()


# =============================================================================
# Server
# =============================================================================


def test_get_server_info(client):
    result = client.get_server_info()

    assert result is not None


# =============================================================================
# Projects
# =============================================================================


def test_get_all_projects(client):
    result = client.get_all_projects()

    assert isinstance(result, list)


def test_get_all_project_files_matching(client):
    pages = list(client.get_all_project_files_matching(env("MC_SEARCH", "test"), page_size=1))

    assert pages is not None


def test_get_project_files_matching(client):
    pages = list(
        client.get_project_files_matching(
            env_int("MC_PROJECT_ID"),
            env("MC_SEARCH", "test"),
            page_size=1,
        )
    )

    assert pages is not None


def test_create_project(client):
    skip_unless_mutating()

    result = client.create_project(
        f"pytest project {datetime.utcnow().isoformat()}",
        CreateProjectRequest(),
    )

    assert result is not None


def test_get_project(client):
    result = client.get_project(env_int("MC_PROJECT_ID"))

    assert result is not None


def test_delete_project(client):
    skip_unless_mutating()

    client.delete_project(env_int("MC_PROJECT_ID"))


def test_update_project(client):
    skip_unless_mutating()

    result = client.update_project(
        env_int("MC_PROJECT_ID"),
        UpdateProjectRequest(),
    )

    assert result is not None


def test_add_user_to_project(client):
    skip_unless_mutating()

    result = client.add_user_to_project(env_int("MC_PROJECT_ID"), env_int("MC_USER_ID"))

    assert result is not None


def test_remove_user_from_project(client):
    skip_unless_mutating()

    result = client.remove_user_from_project(env_int("MC_PROJECT_ID"), env_int("MC_USER_ID"))

    assert result is not None


def test_add_admin_to_project(client):
    skip_unless_mutating()

    result = client.add_admin_to_project(env_int("MC_PROJECT_ID"), env_int("MC_USER_ID"))

    assert result is not None


def test_remove_admin_from_project(client):
    skip_unless_mutating()

    result = client.remove_admin_from_project(env_int("MC_PROJECT_ID"), env_int("MC_USER_ID"))

    assert result is not None


# =============================================================================
# Experiments
# =============================================================================


def test_get_all_experiments(client):
    result = client.get_all_experiments(env_int("MC_PROJECT_ID"))

    assert isinstance(result, list)


def test_get_experiment(client):
    result = client.get_experiment(env_int("MC_EXPERIMENT_ID"))

    assert result is not None


def test_update_experiment(client):
    skip_unless_mutating()

    result = client.update_experiment(
        env_int("MC_EXPERIMENT_ID"),
        UpdateExperimentRequest(),
    )

    assert result is not None


def test_delete_experiment(client):
    skip_unless_mutating()

    client.delete_experiment(env_int("MC_PROJECT_ID"), env_int("MC_EXPERIMENT_ID"))


def test_create_experiment(client):
    skip_unless_mutating()

    result = client.create_experiment(
        env_int("MC_PROJECT_ID"),
        f"pytest experiment {datetime.utcnow().isoformat()}",
        CreateExperimentRequest(),
    )

    assert result is not None


def test_update_experiment_workflows(client):
    skip_unless_mutating()

    result = client.update_experiment_workflows(
        env_int("MC_PROJECT_ID"),
        env_int("MC_EXPERIMENT_ID"),
        env_int("MC_WORKFLOW_ID"),
    )

    assert result is not None


# =============================================================================
# Directories
# =============================================================================


def test_get_directory(client):
    result = client.get_directory(env_int("MC_PROJECT_ID"), env_int("MC_DIRECTORY_ID"))

    assert result is not None


def test_list_directory(client):
    result = client.list_directory(env_int("MC_PROJECT_ID"), env_int("MC_DIRECTORY_ID"))

    assert isinstance(result, list)


def test_list_directory_by_path(client):
    result = client.list_directory_by_path(env_int("MC_PROJECT_ID"), env("MC_DIRECTORY_PATH", "/"))

    assert isinstance(result, list)


def test_create_directory(client):
    skip_unless_mutating()

    result = client.create_directory(
        env_int("MC_PROJECT_ID"),
        f"pytest-directory-{datetime.utcnow().timestamp()}",
        env_int("MC_PARENT_DIRECTORY_ID"),
        CreateDirectoryRequest(),
    )

    assert result is not None


def test_move_directory(client):
    skip_unless_mutating()

    result = client.move_directory(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DIRECTORY_ID"),
        env_int("MC_DEST_DIRECTORY_ID"),
    )

    assert result is not None


def test_rename_directory(client):
    skip_unless_mutating()

    result = client.rename_directory(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DIRECTORY_ID"),
        f"pytest-renamed-directory-{datetime.utcnow().timestamp()}",
    )

    assert result is not None


def test_delete_directory(client):
    skip_unless_mutating()

    client.delete_directory(env_int("MC_PROJECT_ID"), env_int("MC_DIRECTORY_ID"))


def test_update_directory(client):
    skip_unless_mutating()

    result = client.update_directory(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DIRECTORY_ID"),
        UpdateDirectoryRequest(),
    )

    assert result is not None


# =============================================================================
# Files
# =============================================================================


def test_get_file(client):
    result = client.get_file(env_int("MC_PROJECT_ID"), env_int("MC_FILE_ID"))

    assert result is not None


def test_get_file_versions(client):
    result = client.get_file_versions(env_int("MC_PROJECT_ID"), env_int("MC_FILE_ID"))

    assert isinstance(result, list)


def test_set_as_active_file(client):
    skip_unless_mutating()

    result = client.set_as_active_file(env_int("MC_PROJECT_ID"), env_int("MC_FILE_ID"))

    assert result is not None


def test_get_file_by_path(client):
    result = client.get_file_by_path(env_int("MC_PROJECT_ID"), env_required("MC_FILE_PATH"))

    assert result is not None


def test_update_file(client):
    skip_unless_mutating()

    result = client.update_file(
        env_int("MC_PROJECT_ID"),
        env_int("MC_FILE_ID"),
        UpdateFileRequest(),
    )

    assert result is not None


def test_delete_file(client):
    skip_unless_mutating()

    client.delete_file(env_int("MC_PROJECT_ID"), env_int("MC_FILE_ID"), force=True)


def test_move_file(client):
    skip_unless_mutating()

    result = client.move_file(
        env_int("MC_PROJECT_ID"),
        env_int("MC_FILE_ID"),
        env_int("MC_DEST_DIRECTORY_ID"),
    )

    assert result is not None


def test_rename_file(client):
    skip_unless_mutating()

    result = client.rename_file(
        env_int("MC_PROJECT_ID"),
        env_int("MC_FILE_ID"),
        f"pytest-renamed-file-{datetime.utcnow().timestamp()}",
    )

    assert result is not None


def test_download_file(client):
    with tempfile.NamedTemporaryFile(delete=True) as f:
        client.download_file(env_int("MC_PROJECT_ID"), env_int("MC_FILE_ID"), f.name)

        assert os.path.exists(f.name)


def test_download_file_by_path(client):
    with tempfile.NamedTemporaryFile(delete=True) as f:
        client.download_file_by_path(env_int("MC_PROJECT_ID"), env_required("MC_FILE_PATH"), f.name)

        assert os.path.exists(f.name)


def test_upload_file_to_path(client, temp_upload_file):
    skip_unless_mutating()

    result = client.upload_file_to_path(
        env_int("MC_PROJECT_ID"),
        temp_upload_file,
        env("MC_UPLOAD_DEST_PATH", "/pytest-upload.txt"),
    )

    assert result is not None


def test_upload_file(client, temp_upload_file):
    skip_unless_mutating()

    result = client.upload_file(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DIRECTORY_ID"),
        temp_upload_file,
    )

    assert result is not None


def test_upload_bytes(client):
    skip_unless_mutating()

    result = client.upload_bytes(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DIRECTORY_ID"),
        "pytest-upload-bytes.txt",
        io.BytesIO(b"pytest bytes upload\n"),
    )

    assert result is not None


def test_list_files_changed_since(client):
    pages = list(
        client.list_files_changed_since(
            env_int("MC_PROJECT_ID"),
            env("MC_CHANGED_SINCE", "1970-01-01 00:00:00"),
            page_size=1,
        )
    )

    assert pages is not None


# =============================================================================
# Entities
# =============================================================================


def test_get_all_entities(client):
    result = client.get_all_entities(env_int("MC_PROJECT_ID"))

    assert isinstance(result, list)


def test_get_entity(client):
    result = client.get_entity(env_int("MC_PROJECT_ID"), env_int("MC_ENTITY_ID"))

    assert result is not None


def test_create_entity(client):
    skip_unless_mutating()

    result = client.create_entity(
        env_int("MC_PROJECT_ID"),
        f"pytest entity {datetime.utcnow().isoformat()}",
        env_int("MC_ACTIVITY_ID"),
        CreateEntityRequest(),
    )

    assert result is not None


def test_delete_entity(client):
    skip_unless_mutating()

    client.delete_entity(env_int("MC_PROJECT_ID"), env_int("MC_ENTITY_ID"))


def test_create_entity_state(client):
    skip_unless_mutating()

    result = client.create_entity_state(
        env_int("MC_PROJECT_ID"),
        env_int("MC_ENTITY_ID"),
        env_int("MC_ACTIVITY_ID"),
    )

    assert result is not None


# =============================================================================
# Activities
# =============================================================================


def test_get_all_activities(client):
    result = client.get_all_activities(env_int("MC_PROJECT_ID"))

    assert isinstance(result, list)


def test_get_activity(client):
    result = client.get_activity(env_int("MC_PROJECT_ID"), env_int("MC_ACTIVITY_ID"))

    assert result is not None


def test_create_activity(client):
    skip_unless_mutating()

    result = client.create_activity(
        env_int("MC_PROJECT_ID"),
        f"pytest activity {datetime.utcnow().isoformat()}",
        CreateActivityRequest(),
    )

    assert result is not None


def test_delete_activity(client):
    skip_unless_mutating()

    client.delete_activity(env_int("MC_PROJECT_ID"), env_int("MC_ACTIVITY_ID"))


# =============================================================================
# Datasets / published datasets
# =============================================================================


def test_get_all_datasets(client):
    result = client.get_all_datasets(env_int("MC_PROJECT_ID"))

    assert isinstance(result, list)


def test_get_all_published_datasets(client):
    result = client.get_all_published_datasets()

    assert isinstance(result, list)


def test_get_published_dataset(client):
    result = client.get_published_dataset(env_int("MC_PUBLISHED_DATASET_ID"))

    assert result is not None


def test_get_published_dataset_files(client):
    result = client.get_published_dataset_files(env_int("MC_PUBLISHED_DATASET_ID"))

    assert isinstance(result, list)


def test_get_published_dataset_directory(client):
    result = client.get_published_dataset_directory(
        env_int("MC_PUBLISHED_DATASET_ID"),
        env_int("MC_PUBLISHED_DIRECTORY_ID"),
    )

    assert result is not None


def test_list_published_dataset_directory(client):
    result = client.list_published_dataset_directory(
        env_int("MC_PUBLISHED_DATASET_ID"),
        env_int("MC_PUBLISHED_DIRECTORY_ID"),
    )

    assert isinstance(result, list)


def test_list_published_dataset_directory_by_path(client):
    result = client.list_published_dataset_directory_by_path(
        env_int("MC_PUBLISHED_DATASET_ID"),
        env("MC_PUBLISHED_DIRECTORY_PATH", "/"),
    )

    assert isinstance(result, list)


def test_get_published_dataset_entities(client):
    result = client.get_published_dataset_entities(env_int("MC_PUBLISHED_DATASET_ID"))

    assert isinstance(result, list)


def test_get_published_dataset_activities(client):
    result = client.get_published_dataset_activities(env_int("MC_PUBLISHED_DATASET_ID"))

    assert isinstance(result, list)


def test_search_published_data(client):
    result = client.search_published_data(env("MC_SEARCH", "test"))

    assert isinstance(result, list)


def test_get_all_published_dataset_files_matching(client):
    pages = list(client.get_all_published_dataset_files_matching(env("MC_SEARCH", "test"), page_size=1))

    assert pages is not None


def test_get_published_dataset_files_matching(client):
    pages = list(
        client.get_published_dataset_files_matching(
            env_int("MC_PUBLISHED_DATASET_ID"),
            env("MC_SEARCH", "test"),
            page_size=1,
        )
    )

    assert pages is not None


def test_import_dataset(client):
    skip_unless_mutating()

    client.import_dataset(
        env_int("MC_PUBLISHED_DATASET_ID"),
        env_int("MC_PROJECT_ID"),
        f"pytest-import-{datetime.utcnow().timestamp()}",
    )


def test_get_dataset(client):
    result = client.get_dataset(env_int("MC_PROJECT_ID"), env_int("MC_DATASET_ID"))

    assert result is not None


def test_get_dataset_files(client):
    result = client.get_dataset_files(env_int("MC_PROJECT_ID"), env_int("MC_DATASET_ID"))

    assert isinstance(result, list)


def test_get_dataset_entities(client):
    result = client.get_dataset_entities(env_int("MC_PROJECT_ID"), env_int("MC_DATASET_ID"))

    assert isinstance(result, list)


def test_get_dataset_activities(client):
    result = client.get_dataset_activities(env_int("MC_PROJECT_ID"), env_int("MC_DATASET_ID"))

    assert isinstance(result, list)


def test_delete_dataset(client):
    skip_unless_mutating()

    client.delete_dataset(env_int("MC_PROJECT_ID"), env_int("MC_DATASET_ID"))


def test_update_dataset_file_selection(client):
    skip_unless_mutating()

    result = client.update_dataset_file_selection(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DATASET_ID"),
        {},
    )

    assert result is not None


def test_change_dataset_file_selection(client):
    skip_unless_mutating()

    result = client.change_dataset_file_selection(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DATASET_ID"),
        {
            "include_files": [],
            "exclude_files": [],
            "include_dirs": [],
            "exclude_dirs": [],
        },
    )

    assert result is not None


def test_update_dataset_activities(client):
    skip_unless_mutating()

    result = client.update_dataset_activities(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DATASET_ID"),
        env_int("MC_ACTIVITY_ID"),
    )

    assert result is not None


def test_update_dataset_entities(client):
    skip_unless_mutating()

    result = client.update_dataset_entities(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DATASET_ID"),
        env_int("MC_ENTITY_ID"),
    )

    assert result is not None


def test_update_dataset_workflows(client):
    skip_unless_mutating()

    result = client.update_dataset_workflows(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DATASET_ID"),
        env_int("MC_WORKFLOW_ID"),
    )

    assert result is not None


def test_publish_dataset(client):
    skip_unless_mutating()

    result = client.publish_dataset(env_int("MC_PROJECT_ID"), env_int("MC_DATASET_ID"))

    assert result is not None


def test_unpublish_dataset(client):
    skip_unless_mutating()

    result = client.unpublish_dataset(env_int("MC_PROJECT_ID"), env_int("MC_DATASET_ID"))

    assert result is not None


def test_create_dataset(client):
    skip_unless_mutating()

    result = client.create_dataset(
        env_int("MC_PROJECT_ID"),
        f"pytest dataset {datetime.utcnow().isoformat()}",
        CreateDatasetRequest(),
    )

    assert result is not None


def test_update_dataset(client):
    skip_unless_mutating()

    result = client.update_dataset(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DATASET_ID"),
        f"pytest dataset updated {datetime.utcnow().isoformat()}",
        UpdateDatasetRequest(),
    )

    assert result is not None


def test_assign_doi_to_dataset(client):
    skip_unless_mutating()

    result = client.assign_doi_to_dataset(env_int("MC_PROJECT_ID"), env_int("MC_DATASET_ID"))

    assert result is not None


def test_download_published_dataset_zipfile(client):
    with tempfile.NamedTemporaryFile(delete=True) as f:
        client.download_published_dataset_zipfile(env_int("MC_PUBLISHED_DATASET_ID"), f.name)

        assert os.path.exists(f.name)


def test_download_published_dataset_file(client):
    with tempfile.NamedTemporaryFile(delete=True) as f:
        client.download_published_dataset_file(
            env_int("MC_PUBLISHED_DATASET_ID"),
            env_int("MC_PUBLISHED_FILE_ID"),
            f.name,
        )

        assert os.path.exists(f.name)


def test_check_file_in_dataset(client):
    result = client.check_file_in_dataset(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DATASET_ID"),
        env_int("MC_FILE_ID"),
    )

    assert isinstance(result, dict)


def test_check_file_by_path_in_dataset(client):
    result = client.check_file_by_path_in_dataset(
        env_int("MC_PROJECT_ID"),
        env_int("MC_DATASET_ID"),
        env_required("MC_FILE_PATH"),
    )

    assert isinstance(result, dict)


# =============================================================================
# Globus
# =============================================================================


def test_create_globus_upload_request(client):
    skip_unless_mutating()

    result = client.create_globus_upload_request(
        env_int("MC_PROJECT_ID"),
        f"pytest globus upload {datetime.utcnow().isoformat()}",
    )

    assert result is not None


def test_delete_globus_upload_request(client):
    skip_unless_mutating()

    client.delete_globus_upload_request(env_int("MC_PROJECT_ID"), env_int("MC_GLOBUS_UPLOAD_ID"))


def test_finish_globus_upload_request(client):
    skip_unless_mutating()

    result = client.finish_globus_upload_request(
        env_int("MC_PROJECT_ID"),
        env_int("MC_GLOBUS_UPLOAD_ID"),
    )

    assert result is not None


def test_get_all_globus_upload_requests(client):
    result = client.get_all_globus_upload_requests(env_int("MC_PROJECT_ID"))

    assert isinstance(result, list)


def test_create_globus_download_request(client):
    skip_unless_mutating()

    result = client.create_globus_download_request(
        env_int("MC_PROJECT_ID"),
        f"pytest globus download {datetime.utcnow().isoformat()}",
    )

    assert result is not None


def test_delete_globus_download_request(client):
    skip_unless_mutating()

    client.delete_globus_download_request(env_int("MC_PROJECT_ID"), env_int("MC_GLOBUS_DOWNLOAD_ID"))


def test_get_all_globus_download_requests(client):
    result = client.get_all_globus_download_requests(env_int("MC_PROJECT_ID"))

    assert isinstance(result, list)


def test_get_globus_download_request(client):
    result = client.get_globus_download_request(
        env_int("MC_PROJECT_ID"),
        env_int("MC_GLOBUS_DOWNLOAD_ID"),
    )

    assert result is not None


def test_open_globus_transfer(client):
    result = client.open_globus_transfer(env_int("MC_PROJECT_ID"))

    assert result is not None


def test_close_globus_transfer(client):
    skip_unless_mutating()

    client.close_globus_transfer(env_int("MC_PROJECT_ID"))


# =============================================================================
# Users
# =============================================================================


def test_get_user_by_email(client):
    result = client.get_user_by_email(env_required("MC_USER_EMAIL"))

    assert result is not None


def test_get_current_user(client):
    result = client.get_current_user()

    assert result is not None


def test_list_users(client):
    result = client.list_users()

    assert isinstance(result, list)


# =============================================================================
# Communities
# =============================================================================


def test_create_community(client):
    skip_unless_mutating()

    result = client.create_community(
        f"pytest community {datetime.utcnow().isoformat()}",
        CreateCommunityRequest(),
    )

    assert result is not None


def test_get_all_public_communities(client):
    result = client.get_all_public_communities()

    assert isinstance(result, list)


def test_get_all_my_communities(client):
    result = client.get_all_my_communities()

    assert isinstance(result, list)


def test_get_community(client):
    result = client.get_community(env_int("MC_COMMUNITY_ID"))

    assert result is not None


def test_add_dataset_to_community(client):
    skip_unless_mutating()

    result = client.add_dataset_to_community(
        env_int("MC_PUBLISHED_DATASET_ID"),
        env_int("MC_COMMUNITY_ID"),
    )

    assert result is not None


def test_remove_dataset_from_community(client):
    skip_unless_mutating()

    client.remove_dataset_from_community(
        env_int("MC_PUBLISHED_DATASET_ID"),
        env_int("MC_COMMUNITY_ID"),
    )


def test_upload_file_to_community(client, temp_upload_file):
    skip_unless_mutating()

    result = client.upload_file_to_community(temp_upload_file, env_int("MC_COMMUNITY_ID"))

    assert result is not None


def test_delete_file_from_community(client):
    skip_unless_mutating()

    client.delete_file_from_community(
        env_int("MC_COMMUNITY_FILE_ID"),
        env_int("MC_COMMUNITY_ID"),
    )


def test_create_link_in_community(client):
    skip_unless_mutating()

    result = client.create_link_in_community(
        env_int("MC_COMMUNITY_ID"),
        "pytest link",
        env("MC_LINK_URL", "https://example.com"),
        CreateLinkRequest(),
    )

    assert result is not None


def test_delete_link_from_community(client):
    skip_unless_mutating()

    client.delete_link_from_community(
        env_int("MC_COMMUNITY_LINK_ID"),
        env_int("MC_COMMUNITY_ID"),
    )


def test_list_tags_in_community(client):
    result = client.list_tags_in_community(env_int("MC_COMMUNITY_ID"))

    assert result is not None


def test_get_published_datasets_for_author(client):
    result = client.get_published_datasets_for_author(env_required("MC_AUTHOR"))

    assert isinstance(result, list)


def test_get_published_datasets_for_tag(client):
    result = client.get_published_datasets_for_tag(env_required("MC_TAG"))

    assert isinstance(result, list)


def test_list_authors_in_community(client):
    result = client.list_authors_in_community(env_int("MC_COMMUNITY_ID"))

    assert result is not None


# =============================================================================
# Tags / authors
# =============================================================================


def test_list_tags_for_published_datasets(client):
    result = client.list_tags_for_published_datasets()

    assert isinstance(result, list)


def test_list_published_authors(client):
    result = client.list_published_authors()

    assert result is not None


# =============================================================================
# MQL
# =============================================================================


def test_mql_load_project(client):
    client.mql_load_project(env_int("MC_PROJECT_ID"))


def test_mql_reload_project(client):
    client.mql_reload_project(env_int("MC_PROJECT_ID"))


def test_mql_execute_query(client):
    result = client.mql_execute_query(
        env_int("MC_PROJECT_ID"),
        env("MC_MQL_STATEMENT", "select *"),
    )

    assert result is not None