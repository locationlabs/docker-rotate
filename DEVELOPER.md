# Information for developers

## Tox

"tox" is configured to create a source distribution and run flake8 against the code. To invoke it:

    tox

## Integration tests
This project contains some automated integration tests that are designed to be run against a real
Docker instance. They do clean up after themselves, but they are potentially destructive and so
should probably be run in a safe environment.

They test all functionality, but the main thing they're trying to verify are the interactions
between docker-rotate, the docker-py library, and the Docker daemon. Thus they are run with

### Running tests in Vagrant
To run the full suite of tests in Vagrant, make sure you have a working copy of Vagrant, then:

    ./run_vagrant_integration_tests.sh

If the tests fail, they may have left a Vagrant VM running.

### Running tests locally:

To run the integration tests locally:

    tox -e integration_tests

To run the integration tests with a specific docker-py version:

    DOCKER_PY_VERSION='==1.7.0' tox -e integration_tests