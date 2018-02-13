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
upload=${SCRAP}/data
download=${SCRAP}/download

cp -r ${SCRIPTS}/test_data/* ${upload}

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
python -m materials_commons.etl.input.main ${input} --upload ${upload} --rename
echo "-- output script"
python -m materials_commons.etl.output.extract_spreadsheet "Generic Testing" "Test1" ${output} --download $(download)
echo "-- compare script"
python -m materials_commons.etl.output.compare_spreadsheets "Generic Testing" "Test1" ${input} ${output} --upload ${upload} --download $(download)
echo "-- project walker script"
python -m materials_commons.etl.output.project_walker "Generic Testing" "Test1"
echo "-- done"

popd