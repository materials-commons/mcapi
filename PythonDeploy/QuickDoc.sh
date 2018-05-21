#!/usr/bin/env bash
DOCS_GITHUB_BASE=/Users/weymouth/working/MaterialsCommons/workspace/src/github.com/materials-commons/materials-commons.github.io/python-api/sphinx/
NEW_UUID=$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
COMMIT_MESSAGE="Update Python API Docs - $NEW_UUID"
source /Users/weymouth/PythonEnvs/forDocs/bin/activate

rm -rf build

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
rm -rf ${DOCS_GITHUB_BASE}/html
cp -r build/html ${DOCS_GITHUB_BASE}/
pushd ${DOCS_GITHUB_BASE}
git status
git add html
git commit -m "$COMMIT_MESSAGE"
git push
git status
popd
echo "$COMMIT_MESSAGE"