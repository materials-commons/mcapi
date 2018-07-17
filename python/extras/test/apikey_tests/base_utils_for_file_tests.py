from os import environ
from pathlib import Path
from os import path as os_path
from os.path import getsize
from materials_commons.api import api


def _setup_test_filepath1():
    filepath = _make_test_dir_path('fractal.jpg')
    return filepath


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
