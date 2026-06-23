from .decoder import decode_tag_list, decode_dataset_list


class TagMixin:
    def list_tags_for_published_datasets(self):
        """
        List all tags used in published datasets.

        :return: List of tags
        :rtype: Tag[]
        :raises MCAPIError:
        """
        return self._get("/published/tags", decoder=decode_tag_list)

    def list_published_authors(self):
        """
        List all published authors.

        :return: List of author name strings
        :rtype: str[]
        :raises MCAPIError:
        """
        return self._get("/published/authors")

    def get_published_datasets_for_tag(self, tag):
        """
        Get all published datasets tagged with tag.

        :param str tag: tag to use
        :return: List of datasets tagged with tag
        :rtype: Dataset[]
        :raises MCAPIError:
        """
        form = {"tag": tag}
        return self._post("/published/tags/search", form, decoder=decode_dataset_list)

    def get_published_datasets_for_author(self, author):
        """
        Get all published datasets for an author.

        :param str author: Author name string
        :return: List of datasets author is on
        :rtype: Dataset[]
        :raises MCAPIError:
        """
        form = {"author": author}
        return self._post("/published/authors/search", form, decoder=decode_dataset_list)
