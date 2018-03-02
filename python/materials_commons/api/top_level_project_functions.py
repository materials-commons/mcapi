from . import api
from .Project import Project


# -- top level project functions --
def create_project(name, description):
    """
    Creates a new Project object in the database and return it.

    :param name: - the name of the project
    :param description: - a description for the project
    :return: :class:`mcapi.Project`

    >>> name = "A Project"
    >>> description = "This is a project for me"
    >>> project = materials_commons.api.create_project(name, description)
    >>> print(project.name, project.description)

    """
    results = api.create_project(name, description)
    project_id = results['id']
    project = get_project_by_id(project_id)
    return project


def get_project_by_id(project_id):
    """
    Fetch a project from the database and return it/

    :param project_id: the id value for the project
    :return: :class:`mcapi.Project`

    >>> project = get_project_by_id("e4fd5c88-2fb7-40af-b3fc-2711d786e5f6")

    """
    results = api.get_project_by_id(project_id)
    return Project(data=results)


def get_all_projects():
    """
    Return a list of all the project to which the current user has access.

    :return: a list of :class:`mcapi.Project`

    >>> project_list = get_all_projects()
    >>> for project in project_list:
    >>>     print(project.name)

    """
    results = api.projects()
    projects = []
    for r in results:
        projects.append(Project(data=r))
    return projects
