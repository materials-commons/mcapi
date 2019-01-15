class GlobusUploadRequest:
    """
    A Materials Commons Globus Upload Request.

    .. note:: normally created from the database by a call to :func:`mcapi.Project.init_globus_upload_request`
    """

    def __init__(self, data):
        self.id = ""
        self.globus_url = ""
        self.globus_endpoint_id = ""
        self.globus_endpoint_path = ""
        self.input_data = data
        attr = ['id', 'globus_url', 'globus_endpoint_id', 'globus_endpoint_path']
        for a in attr:
            setattr(self, a, data.get(a, None))

    def get_cli_transfer_target(self):
        """
        A helper function to format the string that the Globus CLI expects for a
        transfer target; that is [endpoint-id]:[endpoint-path] .

        :return: String - the destination target suitable for the Globus CLI
        """
        return "{}:{}".format(self.globus_endpoint_id, self.globus_endpoint_path)

    def get_url_transfer_target(self):
        """
        A helper function to format the string that the Globus web app expects
        as a url encoding the destination target for transfer target; with the source
        unspecified.

        :return: String - URL for the Globus Web app; a transfer with the
            source unspecified, and the destination set to the target to Materials Commons
        """
        return self.globus_url
