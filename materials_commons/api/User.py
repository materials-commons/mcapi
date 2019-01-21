from .base import MCObject


class User(MCObject):
    """
    Representing a registered user.

    .. note:: normally created from the database by a call to top level function :func:`mcapi.get_all_users`

    """

    def __init__(self, data=None):
        # normally, from the data base
        self.id = ""
        self.fullname = ""
        self.email = ""

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(User, self).__init__(data)

        attr = ['fullname', 'email']
        for a in attr:
            setattr(self, a, data.get(a, None))

    def can_access(self, project):
        """
        Does this user have permission to access the indicated project.

        :param project: an instance of the :class: `mcapi.Project`
        :return: boolean

        >>> from materials_commons.api import get_all_users
        >>> user_list = get_all_users()
        >>> for user in user_list:
        >>>     if user.can_access(project):
        >>>         print(user.fullname, user.email)

        """
        user_ids = project.get_access_list()
        for id in user_ids:
            if id == self.id:
                return True
        return False
