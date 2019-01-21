from . import api
from .Project import Project
from .make_objects import make_object
from .base import _has_key


# -- top level project functions --
def create_project(name, description, apikey=None):
    """
    Creates a new Project object in the database and return it.

    :param name: - the name of the project
    :param description: - a description for the project
    :return: :class:`mcapi.Project`

    >>> from materials_commons.api import create_project
    >>> name = "A Project"
    >>> description = "This is a project for me"
    >>> project = create_project(name, description)
    >>> print(project.name, project.description)

    """
    results = api.create_project(name, description, apikey=apikey)
    project_id = results['id']
    project = get_project_by_id(project_id, apikey=apikey)
    return project


def get_project_by_id(project_id, apikey=None):
    """
    Fetch a project from the database and return it/

    :param project_id: the id value for the project
    :return: :class:`mcapi.Project`

    >>> from materials_commons.api import get_project_by_id
    >>> project = get_project_by_id("e4fd5c88-2fb7-40af-b3fc-2711d786e5f6")

    """
    results = api.get_project_by_id(project_id, apikey=apikey)
    return Project(data=results, apikey=apikey)


def get_all_projects(apikey=None):
    """
    Return a list of all the project to which the current user has access.

    :return: a list of :class:`mcapi.Project`

    >>> project_list = get_all_projects()
    >>> for project in project_list:
    >>>     print(project.name)

    """
    results = api.projects(apikey=apikey)
    projects = []
    for r in results:
        projects.append(Project(data=r, apikey=apikey))
    return projects


# -- top level user function ---
def get_all_users(apikey=None):
    """
    Return the list of all users registered on the server.

    :return: a list of :class:`mcapi.User`

    >>> user_list = get_all_users()
    >>> for user in user_list:
    >>>     print(user.fullname, user.email)

    """
    results = api.get_all_users(apikey=apikey)
    users = [make_object(u) for u in results['val']]
    return users


# -- top level template function ---
def get_all_templates(apikey=None):
    """
    Return a list of all the templates known to the system.

    :return: a list of :class:`mcapi.Template`

    >>> template_list = get_all_templates()
    >>> for template in template_list:
    >>>     print(template.name, template.id)

    """
    templates_array = api.get_all_templates(apikey=apikey)
    templates = [make_object(t) for t in templates_array]
    return templates


# -- top level functions for experiment etl metadata
def create_experiment_metadata(experiment_id, metadata, apikey=None):
    """
    Create a metadata record for Excel-based experiment workflow ETL.

    :param experiment_id: the id of an existing experiment
    :param metadata: the metadata for the experiment;
        see :class:`materials_commons.etl.input.build_project.BuildProjectExperiment`
    :return: a object of :class:`materials_commons.api.EtlMetadata`
    """
    results = api.create_experiment_metadata(experiment_id, metadata, apikey=apikey)
    if _has_key('error', results):
        # print("Error: ", results['error'])
        return None
    data = results['data']
    data['apikey'] = apikey
    return make_object(data=data)


def get_experiment_metadata_by_experiment_id(experiment_id, apikey=None):
    """
    Fetch an existing metadata record for Excel-based experiment workflow ETL.

    :param experiment_id: the id of an existing experiment
    :return: a object of :class:`materials_commons.api.EtlMetadata`
    """
    results = api.get_experiment_metadata_by_experiment_id(experiment_id, apikey=apikey)
    if _has_key('error', results):
        # print("Error: ", results['error'])
        return None
    data = results['data']
    data['apikey'] = apikey
    return make_object(data=data)


def get_experiment_metadata_by_id(metadata_id, apikey=None):
    """
    Fetch an existing metadata record for Excel-based experiment workflow ETL.

    :param metadata_id: the id of the metadata record
    :return: a object of :class:`materials_commons.api.EtlMetadata`
    """
    results = api.get_experiment_metadata(metadata_id, apikey=apikey)
    if _has_key('error', results):
        # print("Error: ", results['error'])
        return None
    data = results['data']
    data['apikey'] = apikey
    return make_object(data=data)


def get_apikey(email, password):
    """
    Fetch the apikey for the given user

    :param email: user email address
    :param password: user password
    :return: the users apikey string
    """
    return api.get_apikey(email, password)
