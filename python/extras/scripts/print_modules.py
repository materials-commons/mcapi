#!/usr/bin/env python

import pip
for entry in sorted(["%s==%s" % (i.key, i.version) for i in pip.get_installed_distributions()]):
    print(entry)
