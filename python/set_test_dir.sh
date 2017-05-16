#! /bin/bash

pushd test/test_data
export TEST_DATA_DIR=`pwd`
popd
echo "TEST_DATA_DIR=$TEST_DATA_DIR"

export BUILD_DEMO_PROJECT_DATA=$TEST_DATA_DIR/demo_project_data
echo "BUILD_DEMO_PROJECT_DATA=$BUILD_DEMO_PROJECT_DATA"
