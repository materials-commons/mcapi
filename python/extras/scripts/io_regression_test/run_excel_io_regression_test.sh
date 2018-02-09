#!/usr/bin/env bash

set -e

# no-output on pushd and popd
pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

set_locations() {
    # location of this script: extras/scripts/io_regression_test
    SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    pushd ${SCRIPTS}
    BASE="$( cd ../../../ && pwd )"
    popd
}

set_locations

echo "SCRIPTS = $SCRIPTS"
echo "BASE = $BASE"

pushd ${BASE}

SCRAP=/tmp/mc-test
mkdir -p ${SCRAP}/data

input=${SCRAP}/input.xlsx
output=${SCRAP}/output.xlsx
data=${SCRAP}/data

filename=${SCRIPTS}/Generic\ ETL\ Test\ 1.xlsx
echo "-------------- input file = $filename"
cp "$filename" ${input}

echo "-- input"
python -m materials_commons.etl.input.main --input ${input} --dir ${data} --rename
echo "-- output"
python -m materials_commons.etl.output.extract_spreadsheet "Generic Testing" "Test1" --output ${output}
echo "-- compare"
python -m materials_commons.etl.output.compare_spreadsheets "Generic Testing" "Test1" ${input} ${output}
echo "-- done"

popd