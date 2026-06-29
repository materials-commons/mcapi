import io
import os
import tempfile
import uuid

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
# Optional (defaults to production server):
#   MC_BASE_URL
#
# Optional (skip specific test groups if not set):
#   MC_LOGIN_EMAIL / MC_LOGIN_PASSWORD  — login/apikey tests
#   MC_USER_EMAIL                       — get_user_by_email test
#   MC_USER_ID                          — add/remove user/admin on project tests
#   MC_PUBLISHED_DATASET_ID             — published dataset tests
#   MC_PUBLISHED_DIRECTORY_ID           — published dataset directory tests
#   MC_PUBLISHED_FILE_ID                — download published dataset file test
#   MC_GLOBUS_UPLOAD_ID                 — finish_globus_upload_request test
#   MC_COMMUNITY_ID                     — community read/write tests
#   MC_COMMUNITY_FILE_ID                — delete_file_from_community test
#   MC_COMMUNITY_LINK_ID                — delete_link_from_community test
#   MC_AUTHOR                           — get_published_datasets_for_author test
#   MC_TAG                              — get_published_datasets_for_tag test
#   MC_WORKFLOW_ID                      — update_experiment/dataset_workflows tests
#
# All other IDs (project, experiment, directory, file, activity, entity,
# dataset, …) are created automatically by session fixtures and cleaned up
# at the end of the test run.
#
# =============================================================================


# =============================================================================
# Helpers
# =============================================================================


def env(name, default=None):
    return os.getenv(name, default)


def env_optional(name):
    """Return the value of an environment variable, or skip the test if unset."""
    value = os.getenv(name)
    if not value:
        pytest.skip(f"Set {name} to run this test")
    return value


def env_optional_int(name):
    return int(env_optional(name))


def unique_name(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# =============================================================================
# Session fixtures — created once, shared across all tests
# =============================================================================


@pytest.fixture(scope="session")
def client():
    api_key = os.getenv("MC_API_KEY")
    if not api_key:
        pytest.skip("Set MC_API_KEY to run integration tests")
    return Client(
        apikey=api_key,
        base_url=os.getenv("MC_BASE_URL", "https://materialscommons.org/api"),
    )


@pytest.fixture(scope="session")
def project(client):
    """Create a fresh project for the test session and delete it on teardown."""
    proj = client.create_project(unique_name("pytest-project"), CreateProjectRequest())
    proj = client.get_project(proj.id)  # fetch full object so root_dir is populated
    yield proj
    client.delete_project(proj.id)


@pytest.fixture(scope="session")
def root_dir_id(project):
    if project.root_dir is None:
        pytest.skip("Project root_dir not returned by server; cannot determine root directory id")
    return project.root_dir.id


@pytest.fixture(scope="session")
def experiment(client, project):
    exp = client.create_experiment(
        project.id,
        unique_name("pytest-exp"),
        CreateExperimentRequest(),
    )
    yield exp
    # cleaned up when the project is deleted


@pytest.fixture(scope="session")
def test_directory(client, project, root_dir_id):
    d = client.create_directory(
        project.id,
        unique_name("pytest-dir"),
        root_dir_id,
        CreateDirectoryRequest(),
    )
    yield d
    # cleaned up when the project is deleted


@pytest.fixture(scope="session")
def uploaded_file(client, project, root_dir_id):
    """Upload a small text file to the project root and yield its File object."""
    with tempfile.NamedTemporaryFile("wb", suffix=".txt", delete=False) as f:
        f.write(b"pytest test file content\n")
        local_path = f.name
    try:
        result = client.upload_file(project.id, root_dir_id, local_path)
        result = client.get_file(project.id, result.id)  # fetch full object with path
        yield result
    finally:
        os.remove(local_path)
    # remote file is cleaned up when the project is deleted


@pytest.fixture(scope="session")
def activity(client, project):
    act = client.create_activity(
        project.id,
        unique_name("pytest-activity"),
        CreateActivityRequest(),
    )
    yield act
    # cleaned up when the project is deleted


@pytest.fixture(scope="session")
def entity(client, project, activity):
    ent = client.create_entity(
        project.id,
        unique_name("pytest-entity"),
        activity.id,
        CreateEntityRequest(),
    )
    yield ent
    # cleaned up when the project is deleted


@pytest.fixture(scope="session")
def dataset(client, project):
    ds = client.create_dataset(
        project.id,
        unique_name("pytest-dataset"),
        CreateDatasetRequest(),
    )
    yield ds
    client.delete_dataset(project.id, ds.id)


@pytest.fixture()
def temp_upload_file():
    """Create a temporary local file for upload tests; deleted after each test."""
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
    email = env_optional("MC_LOGIN_EMAIL")
    password = env_optional("MC_LOGIN_PASSWORD")
    base_url = env("MC_BASE_URL", "https://materialscommons.org/api")

    api_key = Client.get_apikey(email, password, base_url)

    assert api_key


def test_login():
    email = env_optional("MC_LOGIN_EMAIL")
    password = env_optional("MC_LOGIN_PASSWORD")
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
    pages = list(client.get_all_project_files_matching("test", page_size=1))

    assert pages is not None


def test_get_project_files_matching(client, project):
    pages = list(client.get_project_files_matching(project.id, "test", page_size=1))

    assert pages is not None


def test_create_project(client):
    result = client.create_project(unique_name("pytest-temp-project"), CreateProjectRequest())
    assert result is not None
    client.delete_project(result.id)


def test_get_project(client, project):
    result = client.get_project(project.id)

    assert result is not None


def test_delete_project(client):
    temp = client.create_project(unique_name("pytest-del-project"), CreateProjectRequest())
    client.delete_project(temp.id)


def test_update_project(client, project):
    result = client.update_project(project.id, UpdateProjectRequest(name=project.name, description="new description"))

    assert result is not None


def test_add_user_to_project(client, project):
    user_id = env_optional_int("MC_USER_ID")

    result = client.add_user_to_project(project.id, user_id)

    assert result is not None


def test_remove_user_from_project(client, project):
    user_id = env_optional_int("MC_USER_ID")

    result = client.remove_user_from_project(project.id, user_id)

    assert result is not None


def test_add_admin_to_project(client, project):
    user_id = env_optional_int("MC_USER_ID")

    result = client.add_admin_to_project(project.id, user_id)

    assert result is not None


def test_remove_admin_from_project(client, project):
    user_id = env_optional_int("MC_USER_ID")

    result = client.remove_admin_from_project(project.id, user_id)

    assert result is not None


# =============================================================================
# Experiments
# =============================================================================


def test_get_all_experiments(client, project):
    result = client.get_all_experiments(project.id)

    assert isinstance(result, list)


def test_get_experiment(client, experiment):
    result = client.get_experiment(experiment.id)

    assert result is not None


def test_update_experiment(client, experiment):
    result = client.update_experiment(experiment.id, UpdateExperimentRequest())

    assert result is not None


def test_create_experiment(client, project):
    result = client.create_experiment(
        project.id,
        unique_name("pytest-temp-exp"),
        CreateExperimentRequest(),
    )
    assert result is not None
    client.delete_experiment(project.id, result.id)


def test_delete_experiment(client, project):
    temp = client.create_experiment(
        project.id,
        unique_name("pytest-del-exp"),
        CreateExperimentRequest(),
    )
    client.delete_experiment(project.id, temp.id)


def test_update_experiment_workflows(client, project, experiment):
    workflow_id = env_optional_int("MC_WORKFLOW_ID")

    result = client.update_experiment_workflows(project.id, experiment.id, workflow_id)

    assert result is not None


# =============================================================================
# Directories
# =============================================================================


def test_get_directory(client, project, test_directory):
    result = client.get_directory(project.id, test_directory.id)

    assert result is not None


def test_list_directory(client, project, test_directory):
    result = client.list_directory(project.id, test_directory.id)

    assert isinstance(result, list)


def test_list_directory_by_path(client, project):
    result = client.list_directory_by_path(project.id, "/")

    assert isinstance(result, list)


def test_create_directory(client, project, root_dir_id):
    result = client.create_directory(
        project.id,
        unique_name("pytest-temp-dir"),
        root_dir_id,
        CreateDirectoryRequest(),
    )
    assert result is not None
    client.delete_directory(project.id, result.id)


def test_move_directory(client, project, root_dir_id):
    src = client.create_directory(
        project.id,
        unique_name("pytest-move-src"),
        root_dir_id,
        CreateDirectoryRequest(),
    )
    dest = client.create_directory(
        project.id,
        unique_name("pytest-move-dest"),
        root_dir_id,
        CreateDirectoryRequest(),
    )
    result = client.move_directory(project.id, src.id, dest.id)
    assert result is not None
    # src is now inside dest; both are cleaned up with the project


def test_rename_directory(client, project, root_dir_id):
    temp = client.create_directory(
        project.id,
        unique_name("pytest-rename-dir"),
        root_dir_id,
        CreateDirectoryRequest(),
    )
    result = client.rename_directory(project.id, temp.id, unique_name("pytest-renamed-dir"))
    assert result is not None
    # cleaned up with the project


def test_delete_directory(client, project, root_dir_id):
    temp = client.create_directory(
        project.id,
        unique_name("pytest-del-dir"),
        root_dir_id,
        CreateDirectoryRequest(),
    )
    client.delete_directory(project.id, temp.id)


def test_update_directory(client, project, test_directory):
    result = client.update_directory(project.id, test_directory.id, UpdateDirectoryRequest())

    assert result is not None


# =============================================================================
# Files
# =============================================================================


def test_get_file(client, project, uploaded_file):
    result = client.get_file(project.id, uploaded_file.id)

    assert result is not None


def test_get_file_versions(client, project, uploaded_file):
    result = client.get_file_versions(project.id, uploaded_file.id)

    assert isinstance(result, list)


def test_set_as_active_file(client, project, uploaded_file):
    result = client.set_as_active_file(project.id, uploaded_file.id)

    assert result is not None


def test_get_file_by_path(client, project, uploaded_file):
    result = client.get_file_by_path(project.id, uploaded_file.path)

    assert result is not None


def test_update_file(client, project, uploaded_file):
    result = client.update_file(project.id, uploaded_file.id, UpdateFileRequest())

    assert result is not None


def test_delete_file(client, project, root_dir_id, temp_upload_file):
    f = client.upload_file(project.id, root_dir_id, temp_upload_file)
    client.delete_file(project.id, f.id, force=True)


def test_move_file(client, project, root_dir_id, test_directory, temp_upload_file):
    f = client.upload_file(project.id, root_dir_id, temp_upload_file)
    result = client.move_file(project.id, f.id, test_directory.id)
    assert result is not None
    # moved file cleaned up with the project


def test_rename_file(client, project, root_dir_id, temp_upload_file):
    f = client.upload_file(project.id, root_dir_id, temp_upload_file)
    result = client.rename_file(project.id, f.id, unique_name("pytest-renamed"))
    assert result is not None
    # cleaned up with the project


def test_download_file(client, project, uploaded_file):
    with tempfile.NamedTemporaryFile(delete=True) as f:
        client.download_file(project.id, uploaded_file.id, f.name)
        assert os.path.exists(f.name)


def test_download_file_by_path(client, project, uploaded_file):
    with tempfile.NamedTemporaryFile(delete=True) as f:
        client.download_file_by_path(project.id, uploaded_file.path, f.name)
        assert os.path.exists(f.name)


def test_upload_file_to_path(client, project, temp_upload_file):
    result = client.upload_file_to_path(
        project.id,
        temp_upload_file,
        f"/{unique_name('pytest-upload')}.txt",
    )
    assert result is not None
    # cleaned up with the project


def test_upload_file(client, project, root_dir_id, temp_upload_file):
    result = client.upload_file(project.id, root_dir_id, temp_upload_file)
    assert result is not None
    # cleaned up with the project


def test_upload_bytes(client, project, root_dir_id):
    result = client.upload_bytes(
        project.id,
        root_dir_id,
        unique_name("pytest-bytes") + ".txt",
        io.BytesIO(b"pytest bytes upload\n"),
    )
    assert result is not None
    # cleaned up with the project


def test_list_files_changed_since(client, project):
    pages = list(
        client.list_files_changed_since(project.id, "1970-01-01 00:00:00", page_size=1)
    )
    assert pages is not None


# =============================================================================
# Entities
# =============================================================================


def test_get_all_entities(client, project):
    result = client.get_all_entities(project.id)

    assert isinstance(result, list)


def test_get_entity(client, project, entity):
    result = client.get_entity(project.id, entity.id)

    assert result is not None


def test_create_entity(client, project, activity):
    result = client.create_entity(
        project.id,
        unique_name("pytest-temp-entity"),
        activity.id,
        CreateEntityRequest(),
    )
    assert result is not None
    print("calling delete entity")
    client.delete_entity(project.id, result.id)
    print("past delete entity")


def test_delete_entity(client, project, activity):
    temp = client.create_entity(
        project.id,
        unique_name("pytest-del-entity"),
        activity.id,
        CreateEntityRequest(),
    )
    client.delete_entity(project.id, temp.id)


def test_create_entity_state(client, project, entity, activity):
    result = client.create_entity_state(project.id, entity.id, activity.id)

    assert result is not None


# =============================================================================
# Activities
# =============================================================================


def test_get_all_activities(client, project):
    result = client.get_all_activities(project.id)

    assert isinstance(result, list)


def test_get_activity(client, project, activity):
    result = client.get_activity(project.id, activity.id)

    assert result is not None


def test_create_activity(client, project):
    result = client.create_activity(
        project.id,
        unique_name("pytest-temp-activity"),
        CreateActivityRequest(),
    )
    assert result is not None
    client.delete_activity(project.id, result.id)


def test_delete_activity(client, project):
    temp = client.create_activity(
        project.id,
        unique_name("pytest-del-activity"),
        CreateActivityRequest(),
    )
    client.delete_activity(project.id, temp.id)


# =============================================================================
# Datasets
# =============================================================================


def test_get_all_datasets(client, project):
    result = client.get_all_datasets(project.id)

    assert isinstance(result, list)


def test_get_dataset(client, project, dataset):
    result = client.get_dataset(project.id, dataset.id)

    assert result is not None


def test_get_dataset_files(client, project, dataset):
    result = client.get_dataset_files(project.id, dataset.id)

    assert isinstance(result, list)


def test_get_dataset_entities(client, project, dataset):
    result = client.get_dataset_entities(project.id, dataset.id)

    assert isinstance(result, list)


def test_get_dataset_activities(client, project, dataset):
    result = client.get_dataset_activities(project.id, dataset.id)

    assert isinstance(result, list)


def test_create_dataset(client, project):
    result = client.create_dataset(
        project.id,
        unique_name("pytest-temp-dataset"),
        CreateDatasetRequest(),
    )
    assert result is not None
    client.delete_dataset(project.id, result.id)


def test_delete_dataset(client, project):
    temp = client.create_dataset(
        project.id,
        unique_name("pytest-del-dataset"),
        CreateDatasetRequest(),
    )
    client.delete_dataset(project.id, temp.id)


def test_update_dataset(client, project, dataset):
    result = client.update_dataset(
        project.id,
        dataset.id,
        unique_name("pytest-updated-dataset"),
        UpdateDatasetRequest(),
    )
    assert result is not None


def test_update_dataset_file_selection(client, project, dataset):
    result = client.update_dataset_file_selection(project.id, dataset.id, {})

    assert result is not None


def test_change_dataset_file_selection(client, project, dataset):
    result = client.change_dataset_file_selection(
        project.id,
        dataset.id,
        {
            "include_files": [],
            "exclude_files": [],
            "include_dirs": [],
            "exclude_dirs": [],
        },
    )
    assert result is not None


def test_update_dataset_activities(client, project, dataset, activity):
    result = client.update_dataset_activities(project.id, dataset.id, activity.id)

    assert result is not None


def test_update_dataset_entities(client, project, dataset, entity):
    experiment = client.create_experiment(project.id, unique_name("pytest-update-dataset-entities-experiment"))
    result = client.update_dataset_entities(project.id, dataset.id, entity.id)

    assert result is not None


def test_update_dataset_workflows(client, project, dataset):
    workflow_id = env_optional_int("MC_WORKFLOW_ID")

    result = client.update_dataset_workflows(project.id, dataset.id, workflow_id)

    assert result is not None


def test_publish_dataset(client, project):
    temp = client.create_dataset(
        project.id,
        unique_name("pytest-pub-dataset"),
        CreateDatasetRequest(),
    )
    result = client.publish_dataset(project.id, temp.id)
    assert result is not None
    client.unpublish_dataset(project.id, temp.id)
    client.delete_dataset(project.id, temp.id)


def test_unpublish_dataset(client, project):
    temp = client.create_dataset(
        project.id,
        unique_name("pytest-unpub-dataset"),
        CreateDatasetRequest(),
    )
    client.publish_dataset(project.id, temp.id)
    result = client.unpublish_dataset(project.id, temp.id)
    assert result is not None
    client.delete_dataset(project.id, temp.id)


def test_assign_doi_to_dataset(client, project, dataset):
    result = client.assign_doi_to_dataset(project.id, dataset.id)

    assert result is not None


def test_check_file_in_dataset(client, project, dataset, uploaded_file):
    result = client.check_file_in_dataset(project.id, dataset.id, uploaded_file.id)

    assert isinstance(result, dict)


def test_check_file_by_path_in_dataset(client, project, dataset, uploaded_file):
    result = client.check_file_by_path_in_dataset(project.id, dataset.id, uploaded_file.path)

    assert isinstance(result, dict)


# =============================================================================
# Published datasets  (require MC_PUBLISHED_DATASET_ID)
# =============================================================================


def test_get_all_published_datasets(client):
    result = client.get_all_published_datasets()

    assert isinstance(result, list)


def test_search_published_data(client):
    result = client.search_published_data("test")

    assert isinstance(result, list)


def test_get_all_published_dataset_files_matching(client):
    pages = list(client.get_all_published_dataset_files_matching("test", page_size=1))

    assert pages is not None


def test_get_published_dataset(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")

    result = client.get_published_dataset(dataset_id)

    assert result is not None


def test_get_published_dataset_files(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")

    result = client.get_published_dataset_files(dataset_id)

    assert isinstance(result, list)


def test_get_published_dataset_directory(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")
    directory_id = env_optional_int("MC_PUBLISHED_DIRECTORY_ID")

    result = client.get_published_dataset_directory(dataset_id, directory_id)

    assert result is not None


def test_list_published_dataset_directory(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")
    directory_id = env_optional_int("MC_PUBLISHED_DIRECTORY_ID")

    result = client.list_published_dataset_directory(dataset_id, directory_id)

    assert isinstance(result, list)


def test_list_published_dataset_directory_by_path(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")

    result = client.list_published_dataset_directory_by_path(dataset_id, "/")

    assert isinstance(result, list)


def test_get_published_dataset_entities(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")

    result = client.get_published_dataset_entities(dataset_id)

    assert isinstance(result, list)


def test_get_published_dataset_activities(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")

    result = client.get_published_dataset_activities(dataset_id)

    assert isinstance(result, list)


def test_get_published_dataset_files_matching(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")

    pages = list(client.get_published_dataset_files_matching(dataset_id, "test", page_size=1))

    assert pages is not None


def test_import_dataset(client, project):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")

    client.import_dataset(dataset_id, project.id, unique_name("pytest-import"))


def test_download_published_dataset_zipfile(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")

    with tempfile.NamedTemporaryFile(delete=True) as f:
        client.download_published_dataset_zipfile(dataset_id, f.name)
        assert os.path.exists(f.name)


def test_download_published_dataset_file(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")
    file_id = env_optional_int("MC_PUBLISHED_FILE_ID")

    with tempfile.NamedTemporaryFile(delete=True) as f:
        client.download_published_dataset_file(dataset_id, file_id, f.name)
        assert os.path.exists(f.name)


# =============================================================================
# Globus
# =============================================================================


def test_get_all_globus_upload_requests(client, project):
    result = client.get_all_globus_upload_requests(project.id)

    assert isinstance(result, list)


def test_create_globus_upload_request(client, project):
    result = client.create_globus_upload_request(
        project.id,
        unique_name("pytest-globus-upload"),
    )
    assert result is not None
    client.delete_globus_upload_request(project.id, result.id)


def test_delete_globus_upload_request(client, project):
    temp = client.create_globus_upload_request(
        project.id,
        unique_name("pytest-del-globus-upload"),
    )
    client.delete_globus_upload_request(project.id, temp.id)


def test_finish_globus_upload_request(client, project):
    globus_upload_id = env_optional_int("MC_GLOBUS_UPLOAD_ID")

    result = client.finish_globus_upload_request(project.id, globus_upload_id)

    assert result is not None


def test_get_all_globus_download_requests(client, project):
    result = client.get_all_globus_download_requests(project.id)

    assert isinstance(result, list)


def test_create_globus_download_request(client, project):
    result = client.create_globus_download_request(
        project.id,
        unique_name("pytest-globus-download"),
    )
    assert result is not None
    client.delete_globus_download_request(project.id, result.id)


def test_delete_globus_download_request(client, project):
    temp = client.create_globus_download_request(
        project.id,
        unique_name("pytest-del-globus-download"),
    )
    client.delete_globus_download_request(project.id, temp.id)


def test_get_globus_download_request(client, project):
    temp = client.create_globus_download_request(
        project.id,
        unique_name("pytest-get-globus-download"),
    )
    result = client.get_globus_download_request(project.id, temp.id)
    assert result is not None
    client.delete_globus_download_request(project.id, temp.id)


def test_open_globus_transfer(client, project):
    result = client.open_globus_transfer(project.id)

    assert result is not None


def test_close_globus_transfer(client, project):
    client.open_globus_transfer(project.id)
    client.close_globus_transfer(project.id)


# =============================================================================
# Users
# =============================================================================


def test_get_current_user(client):
    result = client.get_current_user()

    assert result is not None


def test_list_users(client):
    result = client.list_users()

    assert isinstance(result, list)


def test_get_user_by_email(client):
    email = env_optional("MC_USER_EMAIL")

    result = client.get_user_by_email(email)

    assert result is not None


# =============================================================================
# Communities
# =============================================================================


def test_get_all_public_communities(client):
    result = client.get_all_public_communities()

    assert isinstance(result, list)


def test_get_all_my_communities(client):
    result = client.get_all_my_communities()

    assert isinstance(result, list)


def test_create_community(client):
    # Note: there is no delete_community API, so this community persists on the server.
    result = client.create_community(
        unique_name("pytest-community"),
        CreateCommunityRequest(),
    )
    assert result is not None


def test_get_community(client):
    community_id = env_optional_int("MC_COMMUNITY_ID")

    result = client.get_community(community_id)

    assert result is not None


def test_add_dataset_to_community(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")
    community_id = env_optional_int("MC_COMMUNITY_ID")

    result = client.add_dataset_to_community(dataset_id, community_id)

    assert result is not None


def test_remove_dataset_from_community(client):
    dataset_id = env_optional_int("MC_PUBLISHED_DATASET_ID")
    community_id = env_optional_int("MC_COMMUNITY_ID")

    client.remove_dataset_from_community(dataset_id, community_id)


def test_upload_file_to_community(client, temp_upload_file):
    community_id = env_optional_int("MC_COMMUNITY_ID")

    result = client.upload_file_to_community(temp_upload_file, community_id)

    assert result is not None


def test_delete_file_from_community(client):
    community_id = env_optional_int("MC_COMMUNITY_ID")
    file_id = env_optional_int("MC_COMMUNITY_FILE_ID")

    client.delete_file_from_community(file_id, community_id)


def test_create_link_in_community(client):
    community_id = env_optional_int("MC_COMMUNITY_ID")

    result = client.create_link_in_community(
        community_id,
        unique_name("pytest-link"),
        "https://example.com",
        CreateLinkRequest(),
    )
    assert result is not None


def test_delete_link_from_community(client):
    community_id = env_optional_int("MC_COMMUNITY_ID")
    link_id = env_optional_int("MC_COMMUNITY_LINK_ID")

    client.delete_link_from_community(link_id, community_id)


def test_list_tags_in_community(client):
    community_id = env_optional_int("MC_COMMUNITY_ID")

    result = client.list_tags_in_community(community_id)

    assert result is not None


def test_list_authors_in_community(client):
    community_id = env_optional_int("MC_COMMUNITY_ID")

    result = client.list_authors_in_community(community_id)

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


def test_get_published_datasets_for_author(client):
    author = env_optional("MC_AUTHOR")

    result = client.get_published_datasets_for_author(author)

    assert isinstance(result, list)


def test_get_published_datasets_for_tag(client):
    tag = env_optional("MC_TAG")

    result = client.get_published_datasets_for_tag(tag)

    assert isinstance(result, list)


# =============================================================================
# MQL
# =============================================================================


def test_mql_load_project(client, project):
    client.mql_load_project(project.id)


def test_mql_reload_project(client, project):
    client.mql_reload_project(project.id)


def test_mql_execute_query(client, project):
    result = client.mql_execute_query(project.id, "select *")

    assert result is not None
