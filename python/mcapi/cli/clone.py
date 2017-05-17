import sys
import os
import json
import argparse
import mcapi
from mcapi.cli.functions import _proj_path, _proj_config, _print_projects


def clone_subcommand():
    """
    'Clone' a project, i.e. set the local directory tree where files should
    be uploaded/downloaded. Creates a '.mc/config.json'.
    
    mc clone <projid> [--remote <remotename>]
    
    """
    parser = argparse.ArgumentParser(
        description='Clone an existing project',
        prog='mc clone')
    parser.add_argument('id', help='Project id')
    parser.add_argument('--remote', type=str, default='origin', help='Remote name')
    
    # ignore 'mc clone'
    args = parser.parse_args(sys.argv[2:])
    
    remotes = _mc_remotes()
    if not args.remote in remotes:
        print "unrecognized remote:", args.remote
        exit(1)
    remote=remotes[args.remote]
    
    mcapi.set_remote(remote)
    
    project = mcapi.get_project_by_id(args.id)
    
    dest = os.path.join(os.getcwd(), project.name)
    
    if _proj_path(dest) is not None:
        print "mc project already exists at", _proj_path(dest)
        exit(1)
    
    if not os.path.exists(dest):
        os.mkdir(dest)
    os.mkdir(os.path.join(dest,'.mc'))
    with open(_proj_config(dest), 'w') as f:
        # set a default current experiment? 
        data = {'remote_url':remote.config.mcurl, 'project_id': args.id, 'experiment_id': None}
        json.dump(data, f)
    
    print "Cloned project from", remote.config.mcurl, "to", dest
    _print_projects([project])
