import sys
import os
import argparse
from mcapi.cli.functions import make_local_project, _get_file_or_directory

def up_subcommand():
    """
    upload files to Materials Commons
    
    mc up [-r] [<pathspec> ...]
    
    """
    parser = argparse.ArgumentParser(
        description='upload files',
        prog='mc up')
    parser.add_argument('paths', nargs='*', default=None, help='Files or directories')
    parser.add_argument('-r', '--recursive', action="store_true", default=False, help='Upload directory contents recursively')
    parser.add_argument('--limit', nargs=1, type=float, default=[50], help='File size upload limit (MB). Default=50MB.')
    
    # ignore 'mc up'
    args = parser.parse_args(sys.argv[2:])
    
    limit = args.limit[0]
    
    local_abspaths = [os.path.abspath(p) for p in args.paths]
    
    proj = make_local_project()
    
    for p in local_abspaths:
        if os.path.isfile(p):
            #print "uploading:", p
            dir = _get_file_or_directory(proj, os.path.dirname(p))
            if dir is None:
                dir = proj.get_directory(os.path.dirname(_local_to_remote_relpath(proj, p)))
            try:
                result = dir.add_file(os.path.basename(p), p, verbose=True, limit=limit)
            except Exception as e:
                print "Could not upload:", p
                print "Error:"
                print e
            # This should indicate if file already existed on Materials Commons
            #print result.path + ":", result
        elif os.path.isdir(p) and args.recursive:
            #print "uploading:", p
            dir = _get_file_or_directory(proj, os.path.dirname(p))
            if dir is None:
                dir = proj.get_directory(os.path.dirname(_local_to_remote_relpath(proj, p)))
            result, error = dir.add_directory_tree(os.path.basename(p), os.path.dirname(p), verbose=True, limit=limit)
            if len(error):
                for file in error:
                    print "Could not upload:", file
                    print "Error:"
                    print error[file]
                
            #for f in result:
            #    # This should indicate if file already existed on Materials Commons
            #    print f.path + ":", f
        else:
            print "error uploading:", os.path.relpath(p, os.getcwd())
            print "use -r option to upload directory contents, recursively"
    return
