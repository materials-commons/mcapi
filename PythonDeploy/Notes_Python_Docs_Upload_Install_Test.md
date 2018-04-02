```
Notes on testing/upload/install

https://packaging.python.org/tutorials/distributing-packages/
https://packaging.python.org/guides/using-testpypi/
https://packaging.python.org/guides/migrating-to-pypi-org/#uploading

----- set for your system
PYTHON3=/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
PYTHON_ENVS=~/PythonEnvs
MCAPI_BASE=/Users/weymouth/working/MaterialsCommons/workspace/src/github.com/materials-commons/mcapi
SCRAP_TEST_DIR=/Users/weymouth/Desktop/test-python-load
MCAPI_SOURCE=${MCAPI_BASE}/python
SCRAP_DOCS_DIR=/Users/weymouth/Desktop/sphinx_docs
DEPLOY_DIR=${MCAPI_BASE}/PythonDeploy
DOCS_GITHUB_BASE=/Users/weymouth/working/MaterialsCommons/workspace/src/github.com/materials-commons/materials-commons.github.io/python-api/sphinx/

----- set up env with python3 for upload (only needs to be done once) ----
---- Starting NOT in virtual env ----
virtualenv --version
cd ${PYTHON_ENVS}
virtualenv -p ${PYTHON3} forPyPiUpload
source forPyPiUpload/bin/activate
python --version
pip --version
pip install twine

cd ${PYTHON_ENVS}
virtualenv -p ${PYTHON3} forDocs
source forDocs/bin/activate
python --version
pip --version
pip install sphinx
pip install config

----- upload: in env with python3 ---
cd ${MCAPI_BASE}
cd python
source ${PYTHON_ENVS}/forPyPiUpload/bin/activate
python --version
pip --version

rm -r build dist
python setup.py sdist bdist_wheel

twine upload dist/* -r pypitest

Finally:
twine upload dist/*

---- download/test from test PyPI: in any python3 env ---
rm -rf ${SCRAP_TEST_DIR}
mkdir -p ${SCRAP_TEST_DIR}

pushd ~/PythonEnvs
ls
rm -r ~/PythonEnvs/mcdeptest
virtualenv -p python3 mcdeptest
source mcdeptest/bin/activate
popd

cp -r ${DEPLOY_DIR}/install_test/* ${SCRAP_TEST_DIR}/
pushd ${SCRAP_TEST_DIR}
ls
pip install pytest
pip install -r test_requirements.txt
source set_test_dir.sh 
python -m pytest test_workflow.py 
popd

---- download/test from prod PyPI: in any env ---
-- Set up as above, download/test from test PyPI, but change...

pip install -r requirements.txt 
source set_test_dir.sh 
pytest test_workflow.py 

---- set up doc files ---
rm -fr ${SCRAP_DOCS_DIR}
mkdir -p ${SCRAP_DOCS_DIR}

source ${PYTHON_ENVS}/forDocs/bin/activate
cd ${SCRAP_DOCS_DIR}
pwd
cp -r ${MCAPI_SOURCE} source
pushd source
pip install -r requirements.txt
popd
pip uninstall -y materials_commons
pip install materials_commons
sphinx-apidoc -o source -e source/materials_commons/
rm source/modules.rst
rm source/materials_commons.rst
rm source/materials_commons.api.rst
rm source/materials_commons.api.api.rst
rm source/materials_commons.api.base.rst
rm source/materials_commons.api.bulk_file_uploader.rst
rm source/materials_commons.api.config.rst
rm source/materials_commons.api.mc.rst
rm source/materials_commons.api.mc_object_utility.rst
rm source/materials_commons.api.measurement.rst
rm source/materials_commons.api.property_util.rst
rm source/materials_commons.api.remote.rst
rm source/materials_commons.api.version.rst
rm source/materials_commons.etl.*
cp ${DEPLOY_DIR}/docs_started_dir/* ./
cp conf.py index.rst index_api.rst source/
make html
pushd build/html
ls *.html | xargs sed -i '' 's/_sources/site_sources/g'
ls *.html | xargs sed -i '' 's/_static/site_static/g'
ls *.html | xargs sed -i '' 's/_modules/site_modules/g'

ls *.js | xargs sed -i '' 's/_sources/site_sources/g'
ls *.js | xargs sed -i '' 's/_static/site_static/g'
ls *.js | xargs sed -i '' 's/_modules/site_modules/g'

mv _sources site_sources
mv _static site_static
mv _modules site_modules
popd
cp -r build/html ${DOCS_GITHUB_BASE}/
pushd ${DOCS_GITHUB_BASE}
git status
git add html
git commit -m "Update Python API Docs"
git push
git status
popd
```