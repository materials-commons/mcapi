from .client_base import merge_dicts
from .decoder import decode_project, decode_project_list
from .requests import CreateProjectRequest, UpdateProjectRequest


class ProjectMixin:
    def get_all_projects(self, params=None):
        """
        Returns a list of all the projects a user has access to.

        :param params:
        :return: List of projects
        :rtype: Project[]
        :raises MCAPIError:
        """
        return self._get("/projects", params, decoder=decode_project_list)

    def get_all_project_files_matching(self, match, starting_page=None, page_size=None):
        return self._get_files_matching("/projects/files/matching", match, starting_page, page_size)

    def get_project_files_matching(self, project_id, match, starting_page=None, page_size=None):
        return self._get_files_matching(f"/projects/{project_id}/files/matching", match, starting_page, page_size)

    def create_project(self, name, attrs=None):
        """
        Creates a new project for the authenticated user. Project name must be unique.

        :param str name: Name of project
        :param CreateProjectRequest attrs: (optional) Additional attributes for the create request
        :return: The created project
        :rtype: Project
        :raises MCAPIError:
        """
        if not attrs:
            attrs = CreateProjectRequest()
        form = merge_dicts({"name": name}, attrs.to_dict())
        return self._post("/projects", form, decoder=decode_project)

    def get_project(self, project_id, params=None):
        """
        Get a project by its id.

        :param int project_id: Project id for project
        :param params:
        :return: The project
        :rtype: Project
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}", params, decoder=decode_project)

    def delete_project(self, project_id):
        """
        Deletes a project.

        :param int project_id: id of project to delete
        :raises MCAPIError:
        """
        self._delete(f"/projects/{project_id}")

    def update_project(self, project_id, attrs):
        """
        Updates the given project.

        :param int project_id: Id of project to update
        :param UpdateProjectRequest attrs: The attributes to update on the project
        :return: The updated project
        :rtype: Project
        :raises MCAPIError:
        """
        return self._put(f"/projects/{project_id}", attrs.to_dict(), decoder=decode_project)

    def add_user_to_project(self, project_id, user_id):
        """
        Adds user to project.

        :param int project_id: Id of project to add user to
        :param int user_id: Id of user to add to project
        :return: The updated project
        :rtype: Project
        :raises MCAPIError:
        """
        return self._put(f"/projects/{project_id}/add-user/{user_id}", {}, decoder=decode_project)

    def remove_user_from_project(self, project_id, user_id):
        """
        Remove user from project.

        :param int project_id: Id of project to remove user from
        :param int user_id: Id of user to remove from project
        :return: The updated project
        :rtype: Project
        :raises MCAPIError:
        """
        return self._put(f"/projects/{project_id}/remove-user/{user_id}", {}, decoder=decode_project)

    def add_admin_to_project(self, project_id, user_id):
        """
        Adds user as an admin to project.

        :param int project_id: Id of project to add user to
        :param int user_id: Id of user to add to project
        :return: The updated project
        :rtype: Project
        :raises MCAPIError:
        """
        return self._put(f"/projects/{project_id}/add-admin/{user_id}", {}, decoder=decode_project)

    def remove_admin_from_project(self, project_id, user_id):
        """
        Removes admin user from project.

        :param int project_id: Id of project to remove admin from
        :param int user_id: Id of user to remove from project
        :return: The updated project
        :rtype: Project
        :raises MCAPIError:
        """
        return self._put(f"/projects/{project_id}/remove-admin/{user_id}", {}, decoder=decode_project)
