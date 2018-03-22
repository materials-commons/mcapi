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

input=${SCRAP}/input.xlsx
output=${SCRAP}/output.xlsx
upload=${SCRAP}/data
download=${SCRAP}/download

rm -rf ${SCRAP}
mkdir -p ${upload}
mkdir -p ${download}

pushd ${SCRIPTS}
rm -rf test_data
python generate_test_data.py
popd

cp -r ${SCRIPTS}/test_data/data/* ${upload}

filename=${SCRIPTS}/Generic\ ETL\ Test\ 1.xlsx
cp "${filename}" ${input}

echo "--------------"
echo "  starting file = ${filename}"
echo "  input file = ${input}"
echo "  output file = ${output}"
echo "  upload directory = ${upload}"
echo "  download directory = ${download}"
echo "--------------"
echo ""
echo "-- input script"
python -m materials_commons.etl.input_spreadsheet ${input} --upload ${upload} --rename
echo "-- output script"
python -m materials_commons.etl.output_spreadsheet "Generic Testing" "Test1" ${output} --download ${download}
# echo "-- compare script"
# python -m materials_commons.etl.compare_spreadsheets "Generic Testing" "Test1" ${input} ${output} --checksum --upload ${upload} --download ${download}
# echo "-- project walker script"
# python -m materials_commons.etl.project_walker "Generic Testing" "Test1"
# echo "-- done"

popd
