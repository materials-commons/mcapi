from .client_base import merge_dicts
from .decoder import decode_entity, decode_entity_list
from .requests import CreateEntityRequest


class EntityMixin:
    def get_all_entities(self, project_id, params=None):
        """
        Get all entities in a project.

        :param int project_id: The id of the project
        :param params:
        :return: The list of entities
        :rtype: Entity[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/entities", params, decoder=decode_entity_list)

    def get_entity(self, project_id, entity_id, params=None):
        """
        Get an entity.

        :param int project_id: The id of the project containing the entity
        :param int entity_id: The id of the entity
        :param params:
        :return: The entity
        :rtype: Entity
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/entities/{entity_id}", params, decoder=decode_entity)

    def create_entity(self, project_id, name, activity_id, request=None, attrs=None):
        """
        Creates a new entity in the project.

        :param int project_id: The id of the project to create entity in
        :param str name: The entity name
        :param int activity_id: The activity to associate the entity as initially coming from
        :param CreateEntityRequest request: Attributes of the entity
        :param attrs: Array of dicts of the form {"name": "name-of-attr", "unit": "optional-unit", "value": ...}
        :return: The created entity
        :rtype: Entity
        :raises MCAPIError:
        """
        if not request:
            request = CreateEntityRequest()
        if not attrs:
            attrs = []
        form = merge_dicts({
            "name": name,
            "project_id": project_id,
            "attributes": attrs,
            "activity_id": activity_id,
        }, request.to_dict())
        return self._post("/entities", form, decoder=decode_entity)

    def delete_entity(self, project_id, entity_id):
        """
        Delete an entity.

        :param int project_id: The id of the project containing the entity
        :param int entity_id: The entity id
        :raises MCAPIError:
        """
        self._delete(f"/projects/{project_id}/entities/{entity_id}")

    def create_entity_state(self, project_id, entity_id, activity_id, current=True, attrs=None):
        """
        Adds a new state to an existing entity.

        :param int project_id: The id of the project containing the entity
        :param int entity_id: The id of the entity to associate the state with
        :param int activity_id: The id of the activity that created the state
        :param bool current: Whether to mark the state as the current state
        :param attrs: Array of dicts of the form {"name": "name-of-attr", "unit": "optional-unit", "value": ...}
        :return: Entity
        :rtype: Entity
        :raises MCAPIError:
        """
        if not attrs:
            attrs = []
        form = {"current": current, "attributes": attrs}
        return self._post(
            f"/projects/{project_id}/entities/{entity_id}/activities/{activity_id}/create-entity-state",
            form, decoder=decode_entity)
