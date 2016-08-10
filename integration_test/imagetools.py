import io
import json
import textwrap
import time

from docker.errors import NotFound
import pytest


DEFAULT_TEST_IMAGE_NAME = 'locationlabs/zzzdockertestimage'
BASE_IMAGE = "alpine:3.4"


def _normalize_image_id(image_id):
    """
    The image IDs we get back from parsing "docker build output are abbreviated, 12 hex digits long.
    In order to compare them to the ids we get from "docker.Client.images()" calls, we need to
    normalize them
    """
    if image_id is None:
        return None

    if image_id.startswith("sha256:"):
        image_id = image_id[len("sha256:"):]
    return image_id[0:12]


def assert_images(docker_client, *image_ids):
    """
    Verify that, except for the base image used by ImageFactory, only the specifed images exist.
    """
    existing_image_ids = [_normalize_image_id(image["Id"]) for image in docker_client.images()
                          if BASE_IMAGE not in image["RepoTags"]]
    assert set(existing_image_ids) == set(_normalize_image_id(image_id) for image_id in image_ids)
    assert len(existing_image_ids) == len(image_ids)


class ImageFactory:
    def __init__(self, docker_client, name=DEFAULT_TEST_IMAGE_NAME):
        self.docker_client = docker_client
        self.counter = 1
        self.name = name
        self.image_ids = []

    def add(self, tag, *other_tags):
        return self.add_named(self.name, tag, *other_tags)

    def add_named(self, name, tag, *other_tags):

        # The "Created" timestamp on images has 1-second granuarity.
        # So if we create images too quickly, the order of creation won't necessarily match
        # the order we get when we sort containers by the "Created" field - and our unit tests
        # won't do what we expect.
        # So, add an automatic delay to the image factory to avoid this issue.
        # (This is a simple implementation that is guaranteed to do the job. I tried a more complex
        # solution, but I was surprised to see that waiting 1 second is sometimes not enough.)
        if self.counter != 1:
            time.sleep(2)

        dockerfile = textwrap.dedent("""\
            FROM {base_image}
            MAINTAINER Unit Testing

            RUN echo "Test image {name}:{counter}" > /content.txt

            CMD sleep 999
            """.format(base_image=BASE_IMAGE, name=name, counter=self.counter))
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
        self.image_ids.append(image_id)

        for other_tag in other_tags:
            self.docker_client.tag(image_id, name, other_tag, force=True)

        return image_id

    def cleanup(self):
        cleaned = 0
        for image_id in self.image_ids:
            try:
                self.docker_client.remove_image(image_id, force=True)
                cleaned += 1
            except NotFound:
                pass
        return cleaned



