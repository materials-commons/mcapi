import datetime

from .base import MCObject


class GlobusUploadStatus(MCObject):
    """
    A Materials Commons Globus Upload Status record.

    .. note:: normally created from the database by a call to :func:`mcapi.Project.get_globus_upload_status_list`
    """

    def __init__(self, data):
        self.input_data = data
        self.project_id = ""
        self.background_task_id = ""
        self.status = ""
        self.message = ""
        self.user_id = ""
        self.is_ok = False
        self.is_finished = False

        # attr = ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(GlobusUploadStatus, self).__init__(data)
        attr = ['project_id', 'background_task_id', 'status', 'message', 'user_id', 'is_ok', 'is_finished']
        for a in attr:
            setattr(self, a, data.get(a, None))
        self.owner = self.user_id
        self.birthtime = self.convert_status_date(self.birthtime)
        self.mtime = self.convert_status_date(self.mtime)

    def convert_status_date(self, float_seconds):
        timestamp = int(float_seconds)
        return datetime.datetime.utcfromtimestamp(timestamp)
