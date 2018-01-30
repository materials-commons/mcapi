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
THIS_DIR=${MCAPI_BASE}/PythonDeploy

----- set up env with python3 for upload (only needs to be done once) ----
(Starting NOT in virtual env)
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

---- download from test: in any python3 env ---
cd /Users/weymouth/Desktop/test-python-load

pip install -r test_requirements.txt 

source set_test_dir.sh 
pytest test_workflow.py 

---- download from prod: in any env ---
cp -r ${THIS_DIR} ${SCRAP_TEST_DIR}
cd ${SCRAP_TEST_DIR}

pip install -r requirements.txt 

source set_test_dir.sh 
pytest test_workflow.py 

---- set up doc files ---
source ${PYTHON_ENVS}/forDocs/bin/activate
cd /Users/weymouth/working/MaterialsCommons/sphinx/mc-sphinx/docs
rm -rf source build
cp -r /Users/weymouth/working/MaterialsCommons/workspace/src/github.com/materials-commons/mcapi/python source
pushd source
pip install -r requirements.txt
popd
sphinx-apidoc -o source -e source/extras
sphinx-apidoc -o source -e source/materials_commons
rm source/modules.rst
cp conf.py index.rst source/
mkdir source/_static
mkdir source/_templates
make html

--- copy docs to postion in materials-commons.github.io

```