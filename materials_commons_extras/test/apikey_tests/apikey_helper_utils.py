from os import environ
# noinspection PyCompatibility
from pathlib import Path
from os import path as os_path
from os.path import getsize
from materials_commons.api import api


def _setup_test_filepath1():
    filepath = _make_test_dir_path('fractal.jpg')
    return filepath


def _get_filename_from_path(path):
    path = Path(path)
    file_name = path.parts[-1]
    return str(file_name)


def _get_absolute_path_from_path(path):
    path = Path(path)
    return str(path.absolute())


def _get_local_test_dir_path():
    test_path = os_path.abspath(environ['TEST_DATA_DIR'])
    test_file_path = os_path.join(test_path, 'test_upload_data')
    return test_file_path


def _upload_generic_test_file(project_id, apikey):
    results = api.directory_by_id(project_id, 'top', apikey=apikey)
    directory_id = results['id']
    filepath = _original_generic_test_file_path()
    path = Path(filepath)
    file_name = path.parts[-1]
    input_path = str(path.absolute())
    file_raw = api.file_upload(project_id, directory_id, file_name, input_path, apikey=apikey)
    return file_raw


def _original_generic_test_file_path():
    return _setup_test_filepath1()


def _make_test_dir_path(file_name):
    test_path = os_path.abspath(environ['TEST_DATA_DIR'])
    test_file_path = os_path.join(test_path, 'test_upload_data', file_name)
    return test_file_path


def _get_file_size(file_path):
    byte_count = getsize(file_path)
    return byte_count


def make_template_table(templates):
    ret = {}
    for t in templates:
        ret[t.id] = t
    return ret


def find_template_id_from_match(template_table, match):
    found_id = None
    for key in template_table:
        if match in key:
            found_id = key
    return found_id


class FileTestException(BaseException):
    pass
