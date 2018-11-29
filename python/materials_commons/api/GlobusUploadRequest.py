from .base import MCObject


class GlobusUploadRequest(MCObject):
    """
    A Materials Commons Globus Upload Request.

    .. note:: normally created from the database by a call to :func:`mcapi.Project.init_globus_upload_request`
        or any of the other project functions that uploading a file.
    """

    def __init__(self):
        pass

    def is_done(self):
        """
        Query the status of this upload request. Returns true when both these
        conditions are true: globus is finished (successfully) uploading the
        transferred files and those files have been added into Materials Commons

        :return: Boolean - the transfer is (successfully) completed, with all files added

        .. note: This function can return False 'forever' is the transfer is never started
            or if it fails.
        """
        pass

    def get_cli_transfer_target(self):
        """
        A helper function to format the string that the Globus CLI expects for a
        transfer target; that is [endpoint-id]:[endpoint-path] .

        :return: String - the destination target suitable for the Globus CLI
        """
        pass

    def get_url_transfer_target(self):
        """
        A helper function to format the string that the Globus web app expects
        as a url encoding the destination target for transfer target; with the source
        unspecified.

        :return: String - URL for the Globus Web app; a transfer with the
            source unspecified, and the destination set to the target to Materials Commons
        """
        pass