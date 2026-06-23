from .client_base import merge_dicts
from .decoder import decode_community, decode_community_list, decode_tag_list
from .requests import CreateCommunityRequest, CreateLinkRequest


class CommunityMixin:
    def create_community(self, name, attrs=None):
        """
        Creates a new community owned by the user.

        :param str name: Name of community
        :param CreateCommunityRequest attrs: (optional) Additional attributes for the create request
        :return: The created community
        :rtype: Community
        :raises MCAPIError:
        """
        if not attrs:
            attrs = CreateCommunityRequest()
        form = merge_dicts({"name": name}, attrs.to_dict())
        return self._post("/communities", form, decoder=decode_community)

    def get_all_public_communities(self, params=None):
        """
        Get all public communities.

        :param params:
        :return: List of public communities
        :rtype: Community[]
        :raises MCAPIError:
        """
        return self._get('/communities/public', params, decoder=decode_community_list)

    def get_all_my_communities(self, params=None):
        """
        Get all communities owned by user.

        :param params:
        :return: List of communities
        :rtype: Community[]
        :raises MCAPIError:
        """
        return self._get('/communities', params, decoder=decode_community_list)

    def get_community(self, community_id, params=None):
        """
        Get a community.

        :param int community_id: The id of the community to get
        :param params: Query specific parameters
        :return: The Community
        :rtype: Community
        :raises MCAPIError:
        """
        return self._get(f"/communities/{community_id}", params, decoder=decode_community)

    def add_dataset_to_community(self, dataset_id, community_id):
        """
        Add a dataset to a community. The dataset must have been published.

        :param int dataset_id:
        :param int community_id:
        :return: The community with the dataset
        :rtype: Community
        :raises MCAPIError:
        """
        return self._post(f"/communities/{community_id}/datasets/{dataset_id}/add", decoder=decode_community)

    def remove_dataset_from_community(self, dataset_id, community_id):
        """
        Remove a dataset from a community.

        :param int dataset_id:
        :param int community_id:
        :raises MCAPIError:
        """
        self._delete(f"/communities/{community_id}/datasets/{dataset_id}")

    def upload_file_to_community(self, file_path, community_id):
        """
        Uploads a file to a community.

        :param str file_path: path of file to upload
        :param int community_id: The community to upload the file to
        :return: The community
        :rtype: Community
        :raises MCAPIError:
        """
        data = self._upload(f"/communities/{community_id}/upload", file_path)
        return decode_community(data) if data else None

    def delete_file_from_community(self, file_id, community_id):
        """
        Deletes file from the community and removes the file from the system.

        :param int file_id: The file to delete
        :param int community_id: The community to delete it from
        :raises MCAPIError:
        """
        self._delete(f"/communities/{community_id}/files/{file_id}")

    def create_link_in_community(self, community_id, name, url, attrs=None):
        """
        Adds a link to a community.

        :param int community_id: The community to add the link to
        :param str name: name to show for url
        :param str url: url to add
        :param CreateLinkRequest attrs: additional attrs
        :return: The community
        :rtype: Community
        :raises MCAPIError:
        """
        if not attrs:
            attrs = CreateLinkRequest()
        form = merge_dicts({"url": url, "name": name}, attrs.to_dict())
        return self._post(f"/communities/{community_id}/links", form, decoder=decode_community)

    def delete_link_from_community(self, link_id, community_id):
        """
        Delete a link from a community.

        :param int link_id: The link to remove
        :param int community_id: The community to delete the link from
        :raises MCAPIError:
        """
        self._delete(f"/communities/{community_id}/links/{link_id}")

    def list_tags_in_community(self, community_id):
        """
        List all the unique tags across all the published datasets in a community.

        :param int community_id: The community to list the tags for
        :return: The list of tags
        :rtype: Tag[]
        :raises MCAPIError:
        """
        return self._get(f"/communities/{community_id}/tags", decoder=decode_tag_list)

    def list_authors_in_community(self, community_id):
        """
        List all unique authors across all the published datasets in a community.

        :param int community_id: The community to list the authors for
        :return: The list of authors
        :rtype: str[]
        :raises MCAPIError:
        """
        return self._get(f"/communities/{community_id}/authors")
