#!/usr/bin/bash -x
#
# Deploy to PyPi. If there is any argument to the script then it will
# deploy to PyPi. No arguments means deploy to PyPi test.
#
# Usage:
#    ./deploy.sh   # Deploy to PyPi test
#    ./deploy.sh p # Any argument (doesn't have to be p) then deploy to PyPi
#

source ./setup_env.sh

rm -rf ${VENV}
mkdir ${VENV}
cd ${VENV}

python -m venv forPyPiUpload
source forPyPiUpload/bin/activate
pip install twine
pip install wheel

cd ${MCAPI_BASE}
rm -rf build dist
python setup.py sdist bdist_wheel

if [[ $# -gt 0 ]]; then
    if [[ $1 == "p" ]]; then
        twine upload dist/*
    fi
else
    twine upload dist/* -r pypitest
fi

