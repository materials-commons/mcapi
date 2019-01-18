#!/usr/bin/env bash

export VENV=/tmp/MCAPIVENV

export MCAPI_BASE=$(dirname $(pwd))
export SCRAP_TEST_DIR=/tmp/test-python-load

export MCAPI_SOURCE=${MCAPI_BASE}
export SCRAP_DOCS_DIR=/tmp/sphinx-docs

export DEPLOY_DIR=${MCAPI_BASE}/PythonDeploy
export DOCS_GITHUB_BASE=~/workspace/src/github.com/materials-commons/materials-commons.github.io/python-api/sphinx/
