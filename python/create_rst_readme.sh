#!/usr/bin/env bash

pandoc=`which pandoc`

if [ -z $pandoc ]; then
    echo "pandoc (conversion app) is not defined, please install it"
    exit -1
fi

pandoc --from=markdown --to=rst --output=README.rst README.md

echo "README.md copy/converted to README.rst"
