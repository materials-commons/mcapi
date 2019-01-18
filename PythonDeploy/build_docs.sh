#!/usr/bin/bash -x

source ./setup_env.sh

rm -rf ${VENV}
mkdir ${VENV}
cd ${VENV}

virtualenv -p python3 forDocs
source forDocs/bin/activate

pip install sphinx
pip install config

rm -rf ${SCRAP_TEST_DIR}
rm -rf ${SCRAP_DOCS_DIR}

mkdir -p ${SCRAP_TEST_DIR}
mkdir -p ${SCRAP_DOCS_DIR}

cd ${SCRAP_DOCS_DIR}
cp -r ${MCAPI_SOURCE} source
rm -rf source/venv
rm -rf source/PythonDeploy
cd source
pip install -r requirements.txt
python setup.py install
cd ..

sphinx-apidoc -o source -e source/materials_commons/

rm -f source/modules.rst
rm -f source/materials_commons.rst
rm -f source/materials_commons.api.rst
rm -f source/materials_commons.api.api.rst
rm -f source/materials_commons.api.base.rst
rm -f source/materials_commons.api.bulk_file_uploader.rst
rm -f source/materials_commons.api.config.rst
rm -f source/materials_commons.api.mc.rst
rm -f source/materials_commons.api.mc_object_utility.rst
rm -f source/materials_commons.api.measurement.rst
rm -f source/materials_commons.api.property_util.rst
rm -f source/materials_commons.api.remote.rst
rm -f source/materials_commons.api.version.rst
rm -f source/materials_commons.etl.*

cp ${DEPLOY_DIR}/docs_started_dir/* ./
cp conf.py index.rst index_api.rst source/

make html

cd build/html
ls *.html | xargs sed -i 's/_sources/site_sources/g'
ls *.html | xargs sed -i 's/_static/site_static/g'
ls *.html | xargs sed -i 's/_modules/site_modules/g'

ls *.js | xargs sed -i 's/_sources/site_sources/g'
ls *.js | xargs sed -i 's/_static/site_static/g'
ls *.js | xargs sed -i 's/_modules/site_modules/g'

mv _sources site_sources
mv _static site_static
mv _modules site_modules

cd ../..

cp -r build/html ${DOCS_GITHUB_BASE}
pushd ${DOCS_GITHUB_BASE}
#git pull
#git status
#git add html
#git commit -m "Update Python API Docs"
#git push
#git status
popd
