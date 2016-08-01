import pytest

from imagetools import ImageFactory

class ContainerFactory:
    IMAGE_NAME = 'locationlabs/zzzdockertestimage_for_containers'
    IMAGE_TAG = 'image_0'

    def __init__(self, docker_client):
        self.docker_client = docker_client
        self.image_factory = ImageFactory(docker_client, self.IMAGE_NAME)
        self.image_id = self.image_factory.add(self.IMAGE_TAG, "latest")

        self.image_specifier = self.IMAGE_NAME
        self.container_ids = []

    def _create(self, image_specifier=None):
        response = self.docker_client.create_container(
            image=(image_specifier or self.image_specifier))
        return response["Id"]

    def make_created(self, image_specifier=None):
        container_id = self._create(image_specifier)
        self.container_ids.append(container_id)
        return container_id

    def make_running(self, image_specifier=None):
        container_id = self._create(image_specifier)
        self.container_ids.append(container_id)
        self.docker_client.start(container_id)
        return container_id

    def make_stopped(self, image_specifier=None):
        container_id = self._create(image_specifier)
        self.container_ids.append(container_id)
        self.docker_client.start(container_id)

        started = False
        for counter in range(100):
            info = self.docker_client.inspect_container(container_id)
            state = info["State"]["Status"]
            if state == "running":
                started = True
                break
            time.sleep(0.2)
        assert started

        self.docker_client.stop(container_id)

        return container_id

    def cleanup(self):
        # some containers may have already been removed
        container_infos = self.docker_client.containers(all=True)
        existing_container_ids = set(container_info['Id'] for container_info in container_infos)

        for container_id in self.container_ids:
            if container_id in existing_container_ids:
                self.docker_client.remove_container(container_id, force=True)
        self.image_factory.cleanup()
