import sys
import argparse
import json
from tabulate import tabulate
import mcapi
import pandas

def _templates(remote=mcapi.Remote()):
    return mcapi.api.get(remote.make_url_v2('templates'), remote=remote)


def templates_subcommand(argv=sys.argv):
    """
    Show list of process templates
    
    Goal: 
        mc templates [--details] [--remote <remotename> ...] [<templatename> ...]
    
    Current: 
        mc templates [--details] [<templatename> ...]
    """
    parser = argparse.ArgumentParser(
        description='List process templates',
        prog='mc templates')
    parser.add_argument('names', nargs='*', default=None, help='Template names (or id if --id given)')
    parser.add_argument('--id', action="store_true", default=False, help='Input template id instead of name')
    parser.add_argument('--json', action="store_true", default=False, help='Print JSON data')
    
    # ignore 'mc templates'
    args = parser.parse_args(argv[2:])
    
    data = _templates()
    
    # print all templates
    if not args.names:
        
        if args.json:
            print json.dumps(data, indent=2)
        else:
            df = pandas.DataFrame.from_records(data, columns=['name', 'id'])
            print(tabulate(df, showindex=False, headers=['name', 'id']))
    
    # print specific templates
    else:
        if args.id:
            _data = {d['id']:d for d in data}
        else:
            _data = {d['name']:d for d in data}
        
        for name in args.names:
            
            if args.json:
                print json.dumps(_data[name], indent=2)
            else:
                
                print ""
                value_list = ['name', 'description', 'id', 'category', 'process_type', 'destructive', 'does_transform']
                for k in value_list:
                    print k + ":", _data[name][k]
                
                # for 'create sample' processes
                measurements = _data[name]['measurements']
                if len(measurements):
                    print "\nCreate samples with attributes:\n"
                    df = pandas.DataFrame.from_records(measurements, columns=['name', 'attribute', 'otype', 'units'])
                    print(tabulate(df, showindex=False, headers=['name', 'attribute', 'otype', 'units'])) 
                
                # for process settings / attributes
                setup = _data[name]['setup']
                
                # attributes are grouped, for each group print attributes
                for s in setup:
                    properties = s['properties']
                    if len(properties):
                        print "\nProcess attributes: ", s['name'], "\n"
                        df = pandas.DataFrame.from_records(properties, columns=['name', 'attribute', 'otype', 'units'])
                        print(tabulate(df, showindex=False, headers=['name', 'attribute', 'otype', 'units']))
                    
                
    return

