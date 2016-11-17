#!/bin/bash

rm -rf /tmp/source
cp -r /source /tmp/
cd /tmp/source
tox -e integration_test "$@"
