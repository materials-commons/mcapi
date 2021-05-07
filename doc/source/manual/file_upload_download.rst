.. manual/file_upload_download.rst

File Upload and Download
========================

The Materials Commons API supports uploading files. If you have a large number of files, or individual files that are
bigger than 250MB it is recommended that you use Globus to perform your uploads and downloads. Showing how to use the
Globus API is outside the scope of this documentation. ::

    # Create directory off of project root directory
    dir = c.create_directory(project.id, "d1", project.root_dir.id)

    # Upload file in /tmp to newly created directory
    file = c.upload_file(project.id, dir.id, "/tmp/file-to-upload.txt")

    # Download newly uploaded file and write it to a different name in /tmp
    c.download_file(project.id, file.id, "/tmp/newly-downloaded-file.txt")

    # Download file by path on server. Project file paths start with / as their root, so
    # to download the file we uploaded into d1 named file-to-upload.txt it will be located
    # on the server at /d1/file-to-upload.txt.
    c.download_file_by_path(project.id, "/d1/file-to-upload.txt", "/tmp/download-again.txt")

    # Rename the file we previously uploaded from file-to-upload.txt to file.txt
    file = c.rename_file(project.id, file.id, "file.txt")

    # Move the file from the d1 directory to the root directory
    file = c.move_file(project.id, file.id, project.root_dir.id)

    # Delete the uploaded file
    c.delete_file(project.id, file.id)

