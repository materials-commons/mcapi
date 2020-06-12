import materials_commons2 as mcapi
from .exceptions import MCCLIException

def isfile(file_or_dir):
    return isinstance(file_or_dir, mcapi.File) and file_or_dir.mime_type != "directory"

def isdir(file_or_dir):
    return isinstance(file_or_dir, mcapi.File) and file_or_dir.mime_type == "directory"

def get_parent_id(file_or_dir):
    """Get file_or_dir.directory_id, else raise"""
    if hasattr(file_or_dir, 'directory_id'):
        if file_or_dir.directory_id == file_or_dir.id:
            raise MCCLIException("directory_id == id")
        return file_or_dir.directory_id
    else:
        raise MCCLIException("file_or_dir is missing attribute directory_id")
