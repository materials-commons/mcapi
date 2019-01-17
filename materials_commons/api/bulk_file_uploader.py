from multiprocessing import Queue
from threading import Thread, Lock
from os import path as os_path
from os import walk


class BulkFileUploader(object):
    '''
    A utility for uploading entire directory trees.

    :param parallel: boolean - flag indicating that the upload should be multi-threaded
    :param verbose: boolean - flag indicating that trace output should be printed
    :param limit: int - maximum size in MB of files that we be upload
    '''
    def __init__(self, parallel=True, verbose=False, limit=500):
        self.parallel = parallel
        self.verbose = verbose
        self.limit = limit
        self._lock = Lock()
        self._failed_list = []

    def bulk_upload(self, project, local_directory):
        '''
        Upload the entire content of a local_directory using the **projects.local_path** to the base directory;
        that is **project.local_path** is the directory that contains the directory to be uploaded, see example.

        .. note:: This function achieves a speedup of file upload for large directory trees in two ways:
            the directory structure, in the data base, is created prior to any file upload; the uploads
            are (by default) done in parallel with multi-threading. Creating the directory structure
            in advance removes overhead that would normally occur when files are uploaded one at a time.

        :param project: an instance of :class:`mcapi.Project`
        :param local_directory: the directory path (either absolute or relative) of the directory to be uploaded
        :return: a list of paths of the files in the directory that it failed to upload

        >>> project.local_path = "/path/to/Proj"
        >>> local_path = project.local_path + "/data_dir" # a local directory
        >>> loader=BulkFileUploader()
        >>> missed_files = loader.bulk_upload(project, local_path)
        >>> if missed_files:
        >>>     print("The following files were not uploaded --")
        >>>     for path in missed_files:
        >>>         print(path)

        '''
        if not os_path.isdir(local_directory):
            message = "Attempt to upload directory from path that is not a directory: " + local_directory
            raise Exception(message)

        self._failed_list = []

        full_local_dir_path = os_path.abspath(local_directory)
        file_path_list = self._make_file_path_list(full_local_dir_path)

        if len(file_path_list) == 0:
            message = "Attempt to upload directory tree with no files: " + local_directory
            raise Exception(message)

        directory_path_list = []
        for (dirpath, dirnames, filenames) in walk(local_directory):
            db_path = os_path.relpath(dirpath, project.local_path)
            directory_path_list.append('/' + str(db_path))

        directory_table = project.add_directory_list(directory_path_list)

        if self.parallel:
            self._upload_all_parallel(project, directory_table, file_path_list)
        else:
            self._upload_all_sequential(project, directory_table, file_path_list)

        return_list = self._failed_list
        self._failed_list = []

        return return_list

    def _make_dir_list_list(self, tree_dir_path):
        ret = []

        for (dirpath, dirnames, filenames) in walk(tree_dir_path):
            ret.append(dirpath)

        return ret

    def _make_file_path_list(self, tree_dir_path):
        ret = []

        for (dirpath, dirnames, filenames) in walk(tree_dir_path):
            for name in filenames:
                path = os_path.join(dirpath, name)
                ret.append(path)

        return ret

    def _upload_one(self, project, directory, input_path):
        try:
            file_size_mb = os_path.getsize(input_path) >> 20
            if file_size_mb > self.limit:
                msg = "File too large (>{0}MB), skipping. File size = {1}MB" \
                    .format(self.limit, file_size_mb)
                raise BulkFileUploaderSizeException(msg)
            filename = os_path.basename(input_path)
            project.add_file_using_directory(directory, filename, input_path,
                                             verbose=self.verbose, limit=self.limit)
            if self.verbose:
                print("Uploaded " + input_path)
        except Exception as exc:
            if self.verbose:
                print("------------- Exception")
                print(exc)
                print("path = " + str(input_path))
                print("^^^^^^^^^^^^^")
            raise

    def _upload_all_sequential(self, project, directory_table, file_path_list):
        for file_path in file_path_list:
            try:
                db_dir_path = os_path.relpath(os_path.dirname(file_path), project.local_path)
                key = '/' + str(db_dir_path)
                directory = directory_table[key]
                self._upload_one(project, directory, file_path)
            except Exception as exc:
                self._failed_list.append(file_path)

    def _upload_one_parallel(self, q):
        while True:
            packet = q.get()
            try:
                self._upload_one(packet['project'], packet['directory'], packet['path'])
            except Exception as exc:
                with self._lock:
                    self._failed_list.append(packet['path'])
            finally:
                q.task_done()

    def _upload_all_parallel(self, project, directory_table, file_path_list):
        q = Queue(maxsize=100000)
        num_threads = 10

        for i in range(num_threads):
            worker = Thread(target=self._upload_one_parallel, args=(q,))
            worker.setDaemon(True)
            worker.start()

        for file_path in file_path_list:
            db_dir_path = os_path.relpath(os_path.dirname(file_path), project.local_path)
            key = '/' + str(db_dir_path)
            directory = directory_table[key]
            packet = {'project': project, 'directory': directory, 'path': file_path}
            q.put(packet)

        q.join()


class BulkFileUploaderSizeException(Exception):
    pass
