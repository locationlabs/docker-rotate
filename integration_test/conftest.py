
from docker.errors import NotFound
import pytest

import io
import json
import textwrap


@pytest.fixture(scope="module")
def docker_client():
    from docker import Client
    from docker.errors import NotFound
    from docker.utils import kwargs_from_env
    kwargs = kwargs_from_env(assert_hostname=False)
    client = Client(**kwargs)

    # Verify client can talk to server.
    try:
        client.version()
    except NotFound as error:
        raise SystemExit(error)

    return client


DEFAULT_TEST_IMAGE_NAME = 'locationlabs/zzzdockergentestimage'


class ImageFactory:
    def __init__(self, docker_client):
        self.docker_client = docker_client
        self.counter = 1
        self.name = DEFAULT_TEST_IMAGE_NAME
        self.image_ids = []

    def add(self, tag, *other_tags):
        self.add_named(self.name, tag, *other_tags)

    def add_named(self, name, tag, *other_tags):
        dockerfile = textwrap.dedent('''\
            FROM alpine:3.4
            MAINTAINER Unit Testing

            RUN echo "Test image {}:{}" > /content.txt

            CMD sleep 999
            '''.format(name, self.counter))
        dockerfile_bytes = io.BytesIO(dockerfile.encode('utf-8'))

        self.counter += 1
        response_gen = self.docker_client.build(
            fileobj=dockerfile_bytes,
            tag='{}:{}'.format(name, tag),
            rm=True,
            forcerm=True)
        response = [json.loads(line) for line in response_gen]
        response_stream = [obj['stream'][0:-1] for obj in response if 'stream' in obj]

        for line in response_stream:
            print line

        assert response_stream[-1].find('Successfully built') == 0

        # grab and store image id
        image_id = response_stream[-1].rsplit(' ', 1)[1]
        print "--> image id is", image_id
        self.image_ids.append(image_id)

        for other_tag in other_tags:
            self.docker_client.tag(image_id, name, other_tag, force=True)

    def cleanup(self):
        cleaned = 0
        for image_id in self.image_ids:
            try:
                self.docker_client.remove_image(image_id, force=True)
                cleaned += 1
            except NotFound:
                pass
        return cleaned


@pytest.yield_fixture
def image_factory(docker_client):
    factory = ImageFactory(docker_client)
    yield factory
    cleaned = factory.cleanup()
    print "removed", cleaned, "images in image factory cleanup"




