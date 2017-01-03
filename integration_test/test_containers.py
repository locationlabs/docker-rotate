def _totals(docker_client):
    return (len(docker_client.containers()), len(docker_client.containers(all=True)))


def _assert_no_containers(docker_client):
    # common precondition: no existing containers
    assert docker_client.containers(all=True) == []


def _assert_existing(docker_client, *ids):
    existing_container_ids = set(container["Id"] for container
                                 in docker_client.containers(all=True))
    assert existing_container_ids == set(ids)


def _assert_running(docker_client, *ids):
    existing_container_ids = set(container["Id"] for container in docker_client.containers())
    assert existing_container_ids == set(ids)


def test_remove_created_containers(docker_client, container_factory, docker_rotate):

    _assert_no_containers(docker_client)

    c1 = container_factory.make_created()
    c2 = container_factory.make_created()
    r1 = container_factory.make_running()
    s1 = container_factory.make_stopped()
    _assert_existing(docker_client, c1, c2, r1, s1)
    _assert_running(docker_client, r1)

    docker_rotate(['containers', '--created', '0h'])

    _assert_existing(docker_client, r1, s1)
    _assert_running(docker_client, r1)


def test_remove_stopped_containers(docker_client, container_factory, docker_rotate):

    _assert_no_containers(docker_client)

    c1 = container_factory.make_created()
    r1 = container_factory.make_running()
    s1 = container_factory.make_stopped()
    s2 = container_factory.make_stopped()
    _assert_existing(docker_client, c1, r1, s1, s2)
    _assert_running(docker_client, r1)

    docker_rotate(['containers', '--exited', '0h'])

    _assert_existing(docker_client, c1, r1)
    _assert_running(docker_client, r1)


def test_remove_non_running_containers(docker_client, container_factory, docker_rotate):

    _assert_no_containers(docker_client)

    c1 = container_factory.make_created()
    r1 = container_factory.make_running()
    r2 = container_factory.make_running()
    s1 = container_factory.make_stopped()
    s2 = container_factory.make_stopped()
    s3 = container_factory.make_stopped()
    _assert_existing(docker_client, c1, r1, r2, s1, s2, s3)
    _assert_running(docker_client, r1, r2)

    docker_rotate(['containers', '--created', '0h', '--exited', '0h'])

    _assert_existing(docker_client, r1, r2)
    _assert_running(docker_client, r1, r2)


def test_dry_run(docker_client, container_factory, docker_rotate):

    _assert_no_containers(docker_client)

    c1 = container_factory.make_created()
    r1 = container_factory.make_running()
    s1 = container_factory.make_stopped()
    _assert_existing(docker_client, c1, r1, s1)
    _assert_running(docker_client, r1)

    docker_rotate(['--dry-run', 'containers', '--created', '0h', '--exited', '0h'])

    _assert_existing(docker_client, c1, r1, s1)
    _assert_running(docker_client, r1)


def test_time_exclusion(docker_client, container_factory, docker_rotate):

    _assert_no_containers(docker_client)

    c1 = container_factory.make_created()
    r1 = container_factory.make_running()
    s1 = container_factory.make_stopped()
    _assert_existing(docker_client, c1, r1, s1)
    _assert_running(docker_client, r1)

    docker_rotate(['containers', '--created', '5m', '--exited', '5m'])

    _assert_existing(docker_client, c1, r1, s1)
    _assert_running(docker_client, r1)

#
# Name and tag matching for containers was dropped as part of the 3.0 release.
# If we add it back at some point, here are integration tests for it.
#
# def test_name_matching(docker_client, container_factory, docker_rotate):
#
#     CONTAINER_TEST_IMAGE_MATCH_NAME = 'locationlabs/zzzdockertestimage_for_container_matching'
#
#     _assert_no_containers(docker_client)
#
#     container_factory.image_factory.add_named(CONTAINER_TEST_IMAGE_MATCH_NAME, 'latest')
#
#     c1 = container_factory.make_created()
#     r1 = container_factory.make_running()
#     s1 = container_factory.make_stopped()
#     nc1 = container_factory.make_created(CONTAINER_TEST_IMAGE_MATCH_NAME)
#     nr1 = container_factory.make_running(CONTAINER_TEST_IMAGE_MATCH_NAME)
#     ns1 = container_factory.make_stopped(CONTAINER_TEST_IMAGE_MATCH_NAME)
#
#     _assert_existing(docker_client, c1, r1, s1, nc1, nr1, ns1)
#     _assert_running(docker_client, r1, nr1)
#
#     docker_rotate(['containers', '--created', '0m', '--exited', '0m', '--name',
#                    CONTAINER_TEST_IMAGE_MATCH_NAME])
#
#     _assert_existing(docker_client, c1, r1, s1, nr1)
#     _assert_running(docker_client, r1, nr1)
#
#
# def test_inverse_name_matching(docker_client, container_factory, docker_rotate):
#
#     CONTAINER_TEST_IMAGE_MATCH_NAME = 'locationlabs/zzzdockertestimage_for_container_matching'
#
#     _assert_no_containers(docker_client)
#
#     container_factory.image_factory.add_named(CONTAINER_TEST_IMAGE_MATCH_NAME, 'latest')
#
#     c1 = container_factory.make_created()
#     r1 = container_factory.make_running()
#     s1 = container_factory.make_stopped()
#     nc1 = container_factory.make_created(CONTAINER_TEST_IMAGE_MATCH_NAME)
#     nr1 = container_factory.make_running(CONTAINER_TEST_IMAGE_MATCH_NAME)
#     ns1 = container_factory.make_stopped(CONTAINER_TEST_IMAGE_MATCH_NAME)
#     _assert_existing(docker_client, c1, r1, s1, nc1, nr1, ns1)
#     _assert_running(docker_client, r1, nr1)
#
#     docker_rotate(['containers', '--created', '0m', '--exited', '0m', '--name',
#                    "~" + CONTAINER_TEST_IMAGE_MATCH_NAME])
#
#     _assert_existing(docker_client, r1, nc1, nr1, ns1)
#     _assert_running(docker_client, r1, nr1)
#
#
# def test_label_matching(docker_client, container_factory, docker_rotate):
#
#     LABEL = 'other_label'
#
#     _assert_no_containers(docker_client)
#
#     container_factory.image_factory.add(LABEL)
#     image_specifier = '{}:{}'.format(container_factory.image_factory.name, LABEL)
#
#     # create containers with the "latest" label and without
#     c1 = container_factory.make_created()
#     r1 = container_factory.make_running()
#     s1 = container_factory.make_stopped()
#     lc1 = container_factory.make_created(image_specifier)
#     lr1 = container_factory.make_running(image_specifier)
#     ls1 = container_factory.make_stopped(image_specifier)
#
#     _assert_existing(docker_client, c1, r1, s1, lc1, lr1, ls1)
#     _assert_running(docker_client, r1, lr1)
#
#     # clean up containers that are not using the latest image
#     docker_rotate(['containers', '--created', '0m', '--exited', '0m',
#                    '--images', "~:other_label"])
#
#     _assert_existing(docker_client, r1, lc1, lr1, ls1)
#     _assert_running(docker_client, r1, lr1)
