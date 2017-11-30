#!/usr/bin/env python

if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(__file__)))
    from ..api import get_all_templates
    print 'running template2xlsx'
    print get_all_templates()
