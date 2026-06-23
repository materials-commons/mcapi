from .client_base import merge_dicts
from .decoder import decode_activity, decode_activity_list
from .requests import CreateActivityRequest


class ActivityMixin:
    def get_all_activities(self, project_id, params=None):
        """
        Get all activities in a project.

        :param int project_id: The id of the project
        :param params:
        :return: List of activities
        :rtype: Activity[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/activities", params, decoder=decode_activity_list)

    def get_activity(self, project_id, activity_id, params=None):
        """
        Get an activity.

        :param int project_id: The id of the project containing the activity
        :param int activity_id: The id of the activity
        :param params:
        :return: The activity
        :rtype: Activity
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/activities/{activity_id}", params, decoder=decode_activity)

    def create_activity(self, project_id, name, request=None, attrs=None):
        """
        Create a new activity in the project.

        :param int project_id: The project to create the activity in
        :param str name: Name of activity
        :param CreateActivityRequest request: Attributes on the activity
        :param attrs: Array of dicts of the form {"name": "name-of-attr", "unit": "optional-unit", "value": ...}
        :return: The created activity
        :rtype: Activity
        :raises MCAPIError:
        """
        if not request:
            request = CreateActivityRequest()
        if not attrs:
            attrs = []
        form = merge_dicts({"project_id": project_id, "name": name, "attributes": attrs}, request.to_dict())
        return self._post("/activities", form, decoder=decode_activity)

    def delete_activity(self, project_id, activity_id):
        """
        Deletes an activity.

        :param int project_id: The id of the project containing the activity
        :param int activity_id: The id of the activity to delete
        :raises MCAPIError:
        """
        self._delete(f"/projects/{project_id}/activities/{activity_id}")
