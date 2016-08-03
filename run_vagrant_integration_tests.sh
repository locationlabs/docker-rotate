#!/bin/bash

# fail if anything fails.
set -e

function usage() {
   echo "Usage:"
   echo ""
   echo "    $0 -h"
   echo "        show this message"
   echo ""
   echo "    $0"
   echo "        run tests and clean up vagrant environment at the end"
   echo ""
   echo "    $0 --keep"
   echo "        run tests and keep vagrant environment at the end"
}

if [ "$1" == "-h" ] || [ "$1" == "-?" ] || [ "$1" == "--help" ]; then
   usage
   exit 0
elif [ "$1" == "--keep" ] ; then
   keep_virts=yes
elif [ "$1" != "" ] ; then
   echo "Unrecognized option: $1"
   usage
   exit 1
else
   keep_virts=no
fi

echo "--------- Bringing up vagrant boxes"
vagrant up

# Current version of docker-rotate library no longer supports Docker 1.5.0, otherwise
# we'd want to test there too.

echo "--------- Running tests on docker 1.9"
vagrant ssh vagrant-test-docker19 -c 'DOCKER_PY_VERSION="==1.7.0" /source/vagrant/test.sh'

echo "--------- Running tests on docker 1.11"
vagrant ssh vagrant-test-docker111 -c 'DOCKER_PY_VERSION="==1.9.0" /source/vagrant/test.sh'

echo "--------- Running tests on docker 1.12"
vagrant ssh vagrant-test-docker112 -c 'DOCKER_PY_VERSION="==1.9.0" /source/vagrant/test.sh'

if [ "$keep_virts" == "yes" ] ; then
   echo "--------- all tests complete, skipping vagrant env cleanup"
   echo "to clean up the VMs, run \"vagrant destroy\" from this directory."
else 
   echo "--------- all tests complete, tearing down vagrant env"
   vagrant destroy -f
fi