import sys
import os
import argparse
import mcapi
from mcapi.cli.functions import make_local_project, _get_file_or_directory, \
    _obj_path_to_local_path

def down_subcommand():
    """
    download files from Materials Commons
    
    mc down [-r] [<pathspec> ...]
    
    """
    parser = argparse.ArgumentParser(
        description='download files',
        prog='mc down')
    parser.add_argument('paths', nargs='*', default=None, help='Files or directories')
    parser.add_argument('-r', '--recursive', action="store_true", default=False, help='Download directory contents recursively')
    parser.add_argument('-f', '--force', action="store_true", default=False, help='Force overwrite of existing files')
    
    # ignore 'mc down'
    args = parser.parse_args(sys.argv[2:])
    
    local_abspaths = [os.path.abspath(p) for p in args.paths]
    
    proj = make_local_project()
    
    def _check_download(proj_id, file_id, local_path, remote):
        if not os.path.exists(local_path) or args.force:
            dir = os.path.dirname(local_path)
            if not os.path.exists(dir):
                os.makedirs(dir)
            return mcapi.api.file_download(proj_id, file_id, local_path, remote)
        else:
            print "Overwrite '" + os.path.relpath(local_path, os.getcwd()) + "'?"
            while True:
                ans = raw_input('y/n: ')
                if ans == 'y':
                    return mcapi.api.file_download(proj_id, file_id, local_path, remote)
                elif ans == 'n':
                    break
        return None
    
    def _download(proj, dir, recursive=False):
        results = []
        children = dir.get_children()
        for child in children:
            
            if isinstance(child, mcapi.File):
                p = _obj_path_to_local_path(proj, os.path.join(child.parent().path, child.name))
                if not os.path.exists(os.path.dirname(p)):
                    os.makedirs(os.path.dirname(p))
                result_path = _check_download(proj.id, child.id, p, proj.remote)
                if result_path is not None:
                    print "downloaded:", os.path.relpath(result_path, os.getcwd())
                results.append(result_path)
            
            elif isinstance(child, mcapi.Directory) and recursive:
                _download(proj, child, recursive=recursive)
        
        return results
    
    for p in local_abspaths:
        
        if os.path.abspath(p) == proj.path:
            obj = proj.get_top_directory()
        else:
            obj = _get_file_or_directory(proj, p)
        
        if isinstance(obj, mcapi.File):
            #(project_id, file_id, output_file_path, remote=use_remote())
            result_path = _check_download(proj.id, obj.id, p, proj.remote) 
            if result_path is not None:
                print "downloaded:", os.path.relpath(result_path, os.getcwd())
        
        elif isinstance(obj, mcapi.Directory):
            _download(proj, obj, recursive=args.recursive)
    
    return

