from dockerrotate.main import main
from imagetools import assert_images, ImageFactory


def test_no_images_removed(docker_client, image_factory):

    assert_images(docker_client)
    id1 = image_factory.add('image_1', 'latest')
    id2 = image_factory.add('image_2', 'latest')

    main(['images', '--keep', '3'])
    assert_images(docker_client, id1, id2)


def test_no_images_removed_exactly(docker_client, image_factory):

    assert_images(docker_client)
    id1 = image_factory.add('image_1', 'latest')
    id2 = image_factory.add('image_2', 'latest')

    main(['images', '--keep', '2'])
    assert_images(docker_client, id1, id2)


def test_remove_image(docker_client, image_factory):
    assert_images(docker_client)
    id1 = image_factory.add('image_1', 'latest')
    id2 = image_factory.add('image_2', 'latest')
    id3 = image_factory.add('image_3', 'latest')
    id4 = image_factory.add('image_4', 'latest')
    assert_images(docker_client, id1, id2, id3, id4)

    main(['images', '--keep', '2'])
    assert_images(docker_client, id3, id4)


OTHER_TEST_IMAGE_NAME = 'locationlabs/zzzdockergentest_otherimage'


def test_remove_only_matching(docker_client, image_factory):

    assert_images(docker_client)
    id1 = image_factory.add('image_1', 'latest')
    id2 = image_factory.add('image_2', 'latest')
    id3 = image_factory.add('image_3', 'latest')
    id4 = image_factory.add('image_4', 'latest')
    oid1 = image_factory.add_named(OTHER_TEST_IMAGE_NAME, 'image_1', 'latest')
    oid2 = image_factory.add_named(OTHER_TEST_IMAGE_NAME, 'image_2', 'latest')
    oid3 = image_factory.add_named(OTHER_TEST_IMAGE_NAME, 'image_3', 'latest')
    oid4 = image_factory.add_named(OTHER_TEST_IMAGE_NAME, 'image_4', 'latest')
    assert_images(docker_client, id1, id2, id3, id4, oid1, oid2, oid3, oid4)

    # dump images
    print "dumping all images before delete"
    for image in docker_client.images():
        print " - id {}, tag0 {}, created {}".format(
            image["Id"], image["RepoTags"][0], image["Created"])

    main(['images', '--keep', '2', '--name', OTHER_TEST_IMAGE_NAME])

    assert_images(docker_client, id1, id2, id3, id4, oid3, oid4)


def test_skip_removing_old_latest(docker_client, image_factory):

    assert_images(docker_client)
    id1 = image_factory.add('image_1', 'latest')
    id2 = image_factory.add('image_2')
    id3 = image_factory.add('image_3')
    id4 = image_factory.add('image_4')
    assert_images(docker_client, id1, id2, id3, id4)

    # dump images
    print "dumping all images before delete"
    for image in docker_client.images():
        print " - id {}, tag0 {}, created {}".format(
            image["Id"], image["RepoTags"][0], image["Created"])

    # clean up images, but leave latest
    main(['images', '--keep', '2', '--name', image_factory.name, '--tag', '~latest'])

    # check that we have the most recent two plus "latest"
    assert_images(docker_client, id1, id3, id4)


def test_skip_removing_new_latest(docker_client, image_factory):

    assert_images(docker_client)
    id1 = image_factory.add('image_1')
    id2 = image_factory.add('image_2')
    id3 = image_factory.add('image_3')
    id4 = image_factory.add('image_4', 'latest')
    assert_images(docker_client, id1, id2, id3, id4)

    # clean up images, but leave latest
    main(['images', '--keep', '2', '--name', image_factory.name, '--tag', '~latest'])

    # check that we have just the most recent two
    assert_images(docker_client, id3, id4)


def test_skip_removing_in_use(docker_client, container_factory):
    # container factory creates an image when created.
    id1 = container_factory.image_id

    # create a container that uses that image
    container_factory.make_created()

    # create a couple of new images with the same factory
    container_factory.image_factory.add("another_image", "latest")
    id3 = container_factory.image_factory.add("yet_another_image", "latest")

    # clean up images
    main(['images', '--keep', '1'])

    # original should still be there, and most recent, but middle image should be gone.
    assert_images(docker_client, id1, id3)


def test_remove_matching_image(docker_client, image_factory):

    assert_images(docker_client)
    tag = 'image_1'
    id1 = image_factory.add(tag)

    try:
        other_image_factory = ImageFactory(
            docker_client,
            name=OTHER_TEST_IMAGE_NAME,
            base_image="{}:{}".format(image_factory.name, tag))

        id2 = other_image_factory.add('image_2')

        assert_images(docker_client, id1, id2)

        main(['images', '--keep', '0', '--name', image_factory.name])

        assert_images(docker_client, id2)

    finally:
        other_image_factory.cleanup()


def test_remove_matching_image_extra_tag(docker_client, image_factory):

    assert_images(docker_client)
    tag = 'image_1'
    extra_tag = 'also_image_1'
    id1 = image_factory.add(tag, extra_tag)

    try:
        other_image_factory = ImageFactory(
            docker_client,
            name=OTHER_TEST_IMAGE_NAME,
            base_image="{}:{}".format(image_factory.name, tag))

        id2 = other_image_factory.add('image_2')

        assert_images(docker_client, id1, id2)

        main(['images', '--keep', '0', '--name', image_factory.name])

        assert_images(docker_client, id2)

    finally:
        other_image_factory.cleanup()
