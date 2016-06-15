#!/usr/bin/env bash
set -x
set -e
WorkDir=`pwd`
rm -rf ${WorkDir}/venv_test
virtualenv ${WorkDir}/venv_test
source ${WorkDir}/venv_test/bin/activate
cd ${WorkDir}/hydra
pip install pybuilder
pyb install_dependencies
pyb analyze
pyb publish -x run_unit_tests
pyb install -x run_unit_tests
cd $WorkDir
echo "Hydra is now installed inside the virtual enviourenment at ${WordDir}/venv_test"
echo "TO Activate the virtual enviourenment use >source ${WorkDir}/venv_test/bin/activate"
