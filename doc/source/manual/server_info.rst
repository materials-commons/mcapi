.. manual/server_info.rst

Server
======

The API supports querying about the server itself. ::

    server_info = c.get_server_info()

The API lets you the current server version, last date it was updated, the globus endpoint id so you can use globus
for file uploads and downloads, and other meta data information. For more see `Server` class.