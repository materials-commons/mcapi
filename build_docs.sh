#!/usr/bin/env bash
rm -rf doc/build/html
sphinx-apidoc --separate --implicit-namespaces -f -o doc/source/reference/materials_commons materials_commons
python3 setup.py build_sphinx

cd doc/build/html

ls *.html | xargs sed -i 's/_sources/site_sources/g'
ls *.html | xargs sed -i 's/_static/site_static/g'
ls *.html | xargs sed -i 's/_modules/site_modules/g'
ls *.html | xargs sed -i 's/_images/site_images/g'
                                           
ls *.js | xargs sed -i 's/_sources/site_sources/g'
ls *.js | xargs sed -i 's/_static/site_static/g'
ls *.js | xargs sed -i 's/_modules/site_modules/g'

cd reference/materials_commons

ls *.html | xargs sed -i 's/_sources/site_sources/g'
ls *.html | xargs sed -i 's/_static/site_static/g'
ls *.html | xargs sed -i 's/_modules/site_modules/g'
ls *.html | xargs sed -i 's/_images/site_images/g'

cd ../..
cd manual

ls *.html | xargs sed -i 's/_sources/site_sources/g'
ls *.html | xargs sed -i 's/_static/site_static/g'
ls *.html | xargs sed -i 's/_modules/site_modules/g'
ls *.html | xargs sed -i 's/_images/site_images/g'

cd ..
                                           
mv _sources site_sources               
mv _static site_static
mv _modules site_modules
mv _images site_images

