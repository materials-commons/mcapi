from .decoder import decode_server


class ServerMixin:
    def get_server_info(self):
        """
        Gets information about the materials commons server.

        :return: server information
        :rtype: Server
        """
        return self._get("/server/info", decoder=decode_server)
