from .decoder import decode_user, decode_user_list


class UserMixin:
    def get_user_by_email(self, email, params=None):
        """
        Get a user by their email.

        :param str email: email address of user to lookup
        :param params:
        :return: The user
        :rtype: User
        :raises MCAPIError:
        """
        return self._get(f"/users/by-email/{email}", params, decoder=decode_user)

    def get_current_user(self, params=None):
        """
        Get the current user.

        :param params:
        :return: The current user
        :rtype: User
        :raises MCAPIError:
        """
        return self._get(f"/users/by-apikey/{self.apikey}", params, decoder=decode_user)

    def list_users(self, params=None):
        """
        List users of Materials Commons.

        :param params:
        :return: List of users
        :rtype: User[]
        :raises MCAPIError:
        """
        return self._get("/users", params, decoder=decode_user_list)
