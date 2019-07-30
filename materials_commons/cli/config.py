import sys
import os
import json
import argparse

import materials_commons.api as mcapi
import materials_commons.cli.functions as clifuncs


def config_subcommand(argv=sys.argv):
    """
    Configure `mc`

    mc config [--set-globus-endpoint-id <ID>]

    """
    parser = argparse.ArgumentParser(
        description='Configure `mc`',
        prog='mc config')
    parser.add_argument('--set-globus-endpoint-id', type=str, default='', help='Set local globus endpoint ID')
    parser.add_argument('--clear-globus-endpoint-id', action="store_true", default=False, help='Clear local globus endpoint ID')

    # ignore 'mc init'
    args = parser.parse_args(argv[2:])

    if args.set_globus_endpoint_id:
        config = mcapi.Config()
        config.globus.endpoint_id = args.set_globus_endpoint_id[0]
        config.save()

    elif args.clear_globus_endpoint_id:
        config = mcapi.Config()
        config.globus.endpoint_id = None
        config.save()

    else:
        print("No recognized option chosen.")
        exit(1)
