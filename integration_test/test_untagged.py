from dockerrotate.main import main
from imagetools import assert_images

def test_untagged_null_case(docker_client):
    # verify we have no images to start with
    assert_images(docker_client)

    # Run main and verify it doesn't fail
    main(['untagged-images'])


def test_untagged(docker_client, image_factory):
    # add an image, then a second image with the same tag
    # the first image will remain, but untagged.
    id1 = image_factory.add('some_tag')
    id2 = image_factory.add('some_tag')
    assert_images(docker_client, id1, id2)

    main(['untagged-images'])

    # verify that the untagged image was removed
    assert_images(docker_client, id2)


def test_image_in_use(docker_client, container_factory):

    # container factory creates an image when created.
    id1 = container_factory.image_id

    # create a container that uses that image
    cid1 = container_factory.make_created()

    # create a new image with the same factory and the same tags, to make the old image untagged
    id2 = container_factory.image_factory.add(container_factory.IMAGE_TAG, "latest")

    assert_images(docker_client, id1, id2)

    import json
    print "here are the containers at this point"
    for container in docker_client.containers(all=True):
        print json.dumps(container, indent=3)

    main(['untagged-images'])

    # verify that the untagged image was not removed
    assert_images(docker_client, id1, id2)





