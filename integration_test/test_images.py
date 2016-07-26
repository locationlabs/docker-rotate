from dockerrotate.main import main

import pytest


def test_no_images_removed(docker_client):
    # clean up images once
    main(['--use-env', 'images', '--keep', '5'])

    # get number of images
    count = len(docker_client.images(all=False))

    # clean up images again
    main(['--use-env', 'images', '--keep', '5'])

    updated_count = len(docker_client.images(all=False))

    assert updated_count == count


def test_remove_image(docker_client, image_factory):
    # clean up images once
    main(['--use-env', 'images', '--keep', '5'])

    initial_count = len(docker_client.images(all=False))

    for i in range(6):
        image_factory.add('image_{}'.format(i), 'latest')

    post_creation_count = len(docker_client.images())

    assert post_creation_count == initial_count + 6

    # clean up images again
    main(['--use-env', 'images', '--keep', '5'])

    final_count = len(docker_client.images())

    assert final_count == post_creation_count - 1


OTHER_TEST_IMAGE_NAME = 'locationlabs/zzzdockergentest_otherimage'


def _images_with_name(docker_client, image_name):
    return [ image for image in docker_client.images()
             if any(tag.startswith(image_name + ":") for tag in image["RepoTags"])]


def test_remove_only_matching(docker_client, image_factory):

    to_create = 5
    to_keep = 2

    initial_count = len(docker_client.images())

    for i in range(to_create):
        image_factory.add('image_{}'.format(i), 'latest')
        image_factory.add_named(OTHER_TEST_IMAGE_NAME, 'image_{}'.format(i), 'latest')

    post_creation_count = len(docker_client.images())
    assert post_creation_count == initial_count + to_create + to_create

    # clean up images
    main(['--use-env', 'images', '--keep', str(to_keep), '--images', OTHER_TEST_IMAGE_NAME])

    # check that we cleaned up just the ones we care about.
    matching_images = _images_with_name(docker_client, OTHER_TEST_IMAGE_NAME)
    assert len(matching_images) == to_keep

    # check no other images were cleaned
    final_count = len(docker_client.images())
    assert final_count == post_creation_count - (to_create - to_keep)


def test_skip_removing_old_latest(docker_client, image_factory):

    to_create = 5
    to_keep = 2

    initial_count = len(docker_client.images())

    # oldest image is latest
    image_factory.add('image_0', 'latest')
    for i in range(1, to_create):
        image_factory.add('image_{}'.format(i))

    post_creation_count = len(docker_client.images())
    assert post_creation_count == initial_count + to_create

    # clean up images, but leave latest
    main(['--use-env', 'images', '--keep', str(to_keep), '--images', image_factory.name, '~:latest'])

    # check that we still have the right number, plus the latest
    matching_images = _images_with_name(docker_client, image_factory.name)
    assert len(matching_images) == to_keep + 1

    # check that latest is still in there
    latest_tag = "{}:latest".format(image_factory.name)
    assert any(True for image in matching_images if latest_tag in image["RepoTags"])

    # check no other images were cleaned
    final_count = len(docker_client.images())
    assert final_count == post_creation_count - (to_create - to_keep - 1)


def test_skip_removing_new_latest(docker_client, image_factory):

    to_create = 5
    to_keep = 2

    initial_count = len(docker_client.images())

    # normal situation, where newest image is latest
    for i in range(to_create):
        image_factory.add('image_{}'.format(i), 'latest')

    post_creation_count = len(docker_client.images())
    assert post_creation_count == initial_count + to_create

    print "all images for test_skip_removing_new_latest"
    for image in docker_client.images():
        print image["Id"], image["RepoTags"]
    # clean up images, but leave latest
    main(['--use-env', 'images', '--keep', str(to_keep), '--images', image_factory.name, '~:latest'])

    # check that we still have two, plus the latest
    matching_images = _images_with_name(docker_client, image_factory.name)
    print "matching images for test_skip_removing_new_latest"
    for image in matching_images:
        print image["Id"], image["RepoTags"]
    assert len(matching_images) == to_keep + 1

    # check that latest is still in there
    latest_tag = "{}:latest".format(image_factory.name)
    assert any(True for image in matching_images if latest_tag in image["RepoTags"])

    # check no other images were cleaned
    final_count = len(docker_client.images())
    assert final_count == post_creation_count - (to_create - to_keep - 1)





