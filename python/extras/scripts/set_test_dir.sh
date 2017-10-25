#! /bin/bash

# no-output on pushd and popd
pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

set_locations() {
    # location of this script: backend/scripts/testdb
    SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    pushd ${SCRIPTS}
    pushd '..'
    EXTRAS=`pwd`
    popd
    popd
}

set_locations

echo "SCRIPTS = $SCRIPTS"
echo "EXTRAS  = $EXTRAS"

export TEST_DATA_DIR=${EXTRAS}/test/test_data
echo "TEST_DATA_DIR=$TEST_DATA_DIR"

export BUILD_DEMO_PROJECT_DATA=${TEST_DATA_DIR}/demo_project_data
echo "BUILD_DEMO_PROJECT_DATA=$BUILD_DEMO_PROJECT_DATA"

find ${TEST_DATA_DIR} -name ".DS_Store" -exec rm \{\} \;
