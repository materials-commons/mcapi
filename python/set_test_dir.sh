#! /bin/bash

pushd test/test_data
export TEST_DATA_DIR=`pwd`
popd
echo $TEST_DATA_DIR