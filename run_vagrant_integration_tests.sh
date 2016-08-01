#!/bin/bash

# fail if anything fails.
set -e

echo "--------- Bringing up vagrant boxes"
vagrant up

# Current version of the library no longer supports Docker 1.5.0

echo "--------- Running tests on docker 1.9"
vagrant ssh vagrant-test-docker19 -c 'DOCKER_PY_VERSION="==1.7.0" /source/vagrant/test.sh'

echo "--------- Running tests on docker 1.11"
vagrant ssh vagrant-test-docker111 -c 'DOCKER_PY_VERSION="==1.9.0" /source/vagrant/test.sh'

echo "--------- Running tests on docker 1.12"
vagrant ssh vagrant-test-docker112 -c 'DOCKER_PY_VERSION="==1.9.0" /source/vagrant/test.sh'

echo "all tests complete, tearing down vagrant env"

vagrant destroy