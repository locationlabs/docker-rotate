# Information for developers

## Tox

"tox" is configured to create a source distribution, run unit tests, and run flake8 against the
code. To invoke it, make sure you have the "tox" Python library installed, and run:

    tox

## Integration tests
This project contains some automated integration tests. They test functionality, but the main thing
they're trying to verify are the interactions between docker-rotate, the docker-py library, and the
Docker daemon. Thus they are designed to run against a real Docker Engine instance, rather than a
mock.

They are designed to clean up after themselves, but that isn't foolproof, especially if execution
is interrupted. They also assume that they're being run against a Docker Engine instance with no
containers and no images. Thus, overall, it's a good idea to run them in an isolated environment
that can be easily reset.

### Running integration tests in Vagrant
... and that's where Vagrant comes in. [Vagrant](https://www.vagrantup.com/docs/) is a tool for
managing virtual machines on a local system. The project contains a "Vagrantfile" which describes
some virtual machines that can be used for testing, and a script to trigger the tests.

To run the full suite of tests in Vagrant, make sure you have a working copy of Vagrant, then:

    ./run_vagrant_integration_tests.sh

If the tests fail, they will leave the Vagrant VMs running. If the tests succeed, they will tear
down the test VMs, unless you pass the "--keep" argument when you run the tests.

### Running tests locally:

To run the integration tests locally:

    tox -e integration_tests

To run the integration tests with a specific docker-py version:

    DOCKER_PY_VERSION='==1.7.0' tox -e integration_tests