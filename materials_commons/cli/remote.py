import sys
import argparse
from .functions import _mc_remotes
import pandas


def remote_subcommand(argv=sys.argv):
    """
    Show / modify list of known Materials Commons servers.

    Goal:
        mc remote [-v]
        mc remote add
        mc remote remove

    Current:
        mc remote

    """
    parser = argparse.ArgumentParser(
        description='Server settings',
        prog='mc remote')

    # ignore 'mc remote'
    args = parser.parse_args(argv[2:])

    remotes = _mc_remotes()
    data = [{'name': key, 'url': remotes[key].config.mcurl} for key in remotes]
    df = pandas.DataFrame.from_records(data, columns=['name', 'url'])
    print(df.to_string(index=False))
