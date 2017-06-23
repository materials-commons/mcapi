from Queue import Queue
from threading import Thread, Lock
from os import path as os_path
from os import walk


class BulkFileUploader:

    def __init__(self, parallel=True, verbose=False, limit=500):
        """
        A utility for uploading entire directory trees. See :funciton:`bulk_upload`.
        :param parallel: boolean - flag indicating that the upload should be multithreaded
        :param verbose: boolean - flag indicating that trace output should be printed
        :param limit: int - maximum size in MB of files that we be upload
        """
        self.parallel = parallel
        self.verbose = verbose
        self.limit = limit
        self._lock = Lock()
        self._failed_list = []

    def bulk_upload(self, project, local_directory):
        '''
        Upload the entire content of a local_directory using the projects.local_path to the base directory;
        that is project.local_path is the directory that contains the directory to be uploaded.

        .. note This function achieves a speedup of file upload for large directory trees in two ways: the
        directory structure, in the data base, is created prior to any file upload; the uploads are (by default)
        done in parallel with multi-threading. Creating the directory structure in advance removes overhead that
        would normally occur when files are uploaded one at a time.

        :param project: an instance of :class:`mcaip.mc.Project`
        :param local_directory: the directory path (either absolute or relative) of the directory to be uploaded
        :return: a list of files in the directory that failed to upload
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

        if self.parallel:
            self._upload_all_parallel(project, file_path_list)
        else:
            self._upload_all_sequential(project, file_path_list)

        return_list = self._failed_list
        self._failed_list = []

        return return_list

    def _make_file_path_list(self, tree_dir_path):
        ret = []

        for (dirpath, dirnames, filenames) in walk(tree_dir_path):
            for name in filenames:
                path = os_path.join(dirpath, name)
                ret.append(path)

        return ret

    def _upload_one(self, project, input_path):
        try:
            file_size_MB = os_path.getsize(input_path) >> 20
            if file_size_MB > self.limit:
                msg = "File too large (>{0}MB), skipping. File size = {1}MB"\
                    .format(self.limit, file_size_MB)
                raise BulkFileUploaderSizeException(msg)
            project.add_file_by_local_path(input_path)
            if self.verbose:
                print "Uploaded " + input_path
        except Exception as exc:
            if self.verbose:
                print "------------- Exception"
                print exc
                print "path = " + str(input_path)
                print "^^^^^^^^^^^^^"
            raise

    def _upload_all_sequential(self, project, file_path_list):
        for file_path in file_path_list:
            try:
                self._upload_one(project, file_path)
            except Exception:
                self._failed_list.append(file_path)

    def _upload_one_parallel(self, q):
        while True:
            packet = q.get()
            try:
                self._upload_one(packet['project'], packet['path'])
            except Exception as exc:
                if (not isinstance(exc,BulkFileUploaderSizeException)) and packet['retry'] < 3:
                    if self.verbose:
                        "Retrying upload for: " + packet['path']
                    retry = True
                    packet['retry'] += 1
                    q.put(packet)
                else:
                    with self._lock:
                       self._failed_list.append(packet['path'])
            finally:
                q.task_done()

    def _upload_all_parallel(self, project, file_path_list):
        q = Queue(maxsize=100000)
        num_threads = 10

        for i in range(num_threads):
            worker = Thread(target=self._upload_one_parallel, args=(q,))
            worker.setDaemon(True)
            worker.start()

        for file_path in file_path_list:
            packet = {'project': project, 'path': file_path, 'retry': 0}
            q.put(packet)

        q.join()

class BulkFileUploaderSizeException(Exception):
    pass