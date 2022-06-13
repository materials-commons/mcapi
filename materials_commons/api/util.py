import datetime
import os


def to_datetime(dt_str):
    return datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")


def get_date(attr_name, data):
    date = data.get(attr_name, None)
    if date is None:
        return date
    return to_datetime(date)


def get_file_path(path, project_id=None, c=None):
    """
    Gets the path for a file. If project_id, c, and the environment
    variable MCFS_DIR are all set, then get_file_path() assumes it
    is running on the Materials Commons server and returns the path
    to the file stored in Materials Commons storage. Otherwise it
    assumes it is running in a local environment and just returns
    the path sent in.

    This function allows developers to create tools that will run
    on the Materials Commons server, but test them locally. It is
    recommended that all paths be relative paths with the
    assumption that the tool is running in the project root.

    :param str path: Path for file to look up
    :param int|None project_id: If set the project_id the file is in
    :param Client|None: The materials_commons.api.Client client
    :return: The file path
    :rtype: str
    :raises MCAPIError:
    """
    if c is None:
        return path
    if project_id is None:
        return path
    mcfs_dir = os.getenv("MCFS_DIR")
    if mcfs_dir is None:
        return path
    p = os.path.normpath(os.path.join("/", path))
    f = c.get_file_by_path(project_id, p)
    uuid_parts = f.uuid.split("-")
    return os.path.join(mcfs_dir, uuid_parts[1][0:2], uuid_parts[1][2:4], f.uuid)
