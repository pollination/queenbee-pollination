#!/bin/sh

echo "Building distribution"
python setup.py sdist bdist_wheel
echo "Pushing new version to PyPi"
twine upload dist/* -u $PYPI_USER -p $PYPI_PASSWORD