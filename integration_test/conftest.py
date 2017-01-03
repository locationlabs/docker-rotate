"""
Contains pytest fixtures to be used by tests.
"""
from docker import Client
from docker.utils import kwargs_from_env
import pytest

from dockerrotate.main import main as docker_rotate_main
from imagetools import ImageFactory
from containertools import ContainerFactory


def pytest_addoption(parser):
    parser.addoption("--client-version",
                     help="Specify Docker client version to use.",
                     default=None)


@pytest.fixture(scope="module")
def docker_client(pytestconfig):
    kwargs = kwargs_from_env(assert_hostname=False)
    version = pytestconfig.getoption("--client-version")
    if version is not None:
        kwargs["version"] = version
    client = Client(**kwargs)

    # Verify client can talk to server.
    # If not, we'll see NotFound here and testing will stop.
    client.version()

    return client


@pytest.fixture
def docker_rotate(pytestconfig):
    """A wrapper around dockerrotate.main that injects --client-version when supplied."""
    def _docker_rotate(args):
        version = pytestconfig.getoption("--client-version")
        if "--client-version" not in args and version is not None:
            args = ["--client-version", version] + args

        return docker_rotate_main(args)

    return _docker_rotate


@pytest.yield_fixture
def image_factory(docker_client):
    factory = ImageFactory(docker_client)
    yield factory
    cleaned = factory.cleanup()
    print "removed", cleaned, "images in image factory cleanup"


@pytest.yield_fixture
def container_factory(docker_client):
    factory = ContainerFactory(docker_client)
    yield factory
    factory.cleanup()
