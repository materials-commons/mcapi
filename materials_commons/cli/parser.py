# temporary home before integrating else where
from __future__ import unicode_literals
import sys
import argparse
from ..api import _Config
from .remote import remote_subcommand
from .proj import ProjSubcommand
from .expt import expt_subcommand
from .init import init_subcommand
from .clone import clone_subcommand
from .ls import ls_subcommand
from .up import up_subcommand
from .down import down_subcommand
from .templates import TemplatesSubcommand
from .proc import ProcSubcommand
from .samp import SampSubcommand
from io import StringIO
import imp


class CommonsCLIParser(object):

    standard_usage = [
        {'name': 'remote', 'desc': 'List servers', 'subcommand': remote_subcommand},
        {'name': 'proj', 'desc': 'List projects', 'subcommand': ProjSubcommand()},
        {'name': 'expt', 'desc': 'List, create, delete, and modify experiments', 'subcommand': expt_subcommand},
        {'name': 'init', 'desc': 'Initialize a new project', 'subcommand': init_subcommand},
        {'name': 'clone', 'desc': 'Clone an existing project', 'subcommand': clone_subcommand},
        {'name': 'ls', 'desc': 'List local and remote directory contents', 'subcommand': ls_subcommand},
        {'name': 'up', 'desc': 'Upload files', 'subcommand': up_subcommand},
        {'name': 'down', 'desc': 'Download files', 'subcommand': down_subcommand},
        {'name': 'templates', 'desc': 'List process templates', 'subcommand': TemplatesSubcommand()},
        {'name': 'proc', 'desc': 'List processes', 'subcommand': ProcSubcommand()},
        {'name': 'samp', 'desc': 'List samples', 'subcommand': SampSubcommand()}
    ]

    def __init__(self, argv):

        usage_help = StringIO()
        usage_help.write("mc <command> [<args>]\n\n")
        usage_help.write("The standard mc commands are:\n")

        for interface in CommonsCLIParser.standard_usage:
            usage_help.write("  {:10} {:40}\n".format(interface['name'], interface['desc']))
        standard_interfaces = {d['name']: d for d in CommonsCLIParser.standard_usage}

        # read custom interfaces from config file
        config = _Config()
        custom_interfaces = {d['name']: d for d in config.interfaces}
        if len(config.interfaces):
            usage_help.write("\nSpecialized commands are:\n")
        for interface in config.interfaces:
            usage_help.write("  {:10} {:40}\n".format(interface['name'], interface['desc']))

        parser = argparse.ArgumentParser(
            description='Materials Commons command line interface',
            usage=usage_help.getvalue())
        parser.add_argument('command', help='Subcommand to run')

        if len(argv) < 2:
            parser.print_help()
            return

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(argv[1:2])

        if hasattr(self, args.command):
            getattr(self, args.command)(argv)
        elif args.command in standard_interfaces:
            standard_interfaces[args.command]['subcommand'](argv)
        elif args.command in custom_interfaces:
            # load module and run command
            modulename = custom_interfaces[args.command]['module']
            subcommandname = custom_interfaces[args.command]['subcommand']
            f, filename, description = imp.find_module(modulename)
            try:
                module = imp.load_module(modulename, f, filename, description)
                getattr(module, subcommandname)(argv)
            finally:
                if f:
                    f.close()

        else:
            print('Unrecognized command')
            parser.print_help()
            exit(1)
