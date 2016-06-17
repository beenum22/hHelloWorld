#!/usr/bin/env bash
set -x
set -e
WorkDir=`pwd`
publisher_port=$1
num_msgs=$2
${WorkDir}/src/hw_test.py ${publisher_port} ${num_msgs}
