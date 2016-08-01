"""
Contains pytest fixtures to be used by tests.
"""
from docker import Client
from docker.utils import kwargs_from_env
import pytest

from imagetools import ImageFactory
from containertools import ContainerFactory


@pytest.fixture(scope="module")
def docker_client():
    kwargs = kwargs_from_env(assert_hostname=False)
    client = Client(**kwargs)

    # Verify client can talk to server.
    # If not, we'll see NotFound here and testing will stop.
    client.version()

    return client


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
