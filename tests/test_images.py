import pytest

from dockerrotate.images import determine_images_to_remove, find_image_ids_to_keep
from dockerrotate.main import parse_arguments

from utils import image_entry, created_container_entry, containers_result, mins_ago


IID1 = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb01"
IID2 = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb02"
IID3 = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb03"
IID4 = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb04"
IID5 = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb05"
IID6 = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb06"
IID7 = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb07"

CID1 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc01"
CID2 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc02"
CID3 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc03"
CID4 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc04"
CID5 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc05"
CID6 = "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc06"


def _assert_ids(images, *image_ids):
    assert set(image["Id"] for image in images) == set(image_ids)

    # make sure there aren't repeats in the list to delete, too.
    assert len(images) == len(image_ids)


def test_keep_two():
    images = [
        image_entry(IID1, mins_ago(200), "foo:v1.1"),
        image_entry(IID2, mins_ago(190), "foo:v1.2"),
        image_entry(IID3, mins_ago(180), "foo:v1.3"),
        image_entry(IID4, mins_ago(170), "foo:v1.4", "foo:latest"),
    ]
    args = parse_arguments(['images', '--keep', '2'])
    result = determine_images_to_remove(images, [], args)
    _assert_ids(result, IID1, IID2)


def test_keep_zero():
    images = [
        image_entry(IID1, mins_ago(200), "foo:v1.1"),
        image_entry(IID2, mins_ago(190), "foo:v1.2"),
        image_entry(IID3, mins_ago(180), "foo:v1.3"),
        image_entry(IID4, mins_ago(170), "foo:v1.4", "foo:latest"),
    ]
    args = parse_arguments(['images', '--keep', '0'])

    ids_to_keep = find_image_ids_to_keep(images, args)
    assert ids_to_keep == set()

    result = determine_images_to_remove(images, [], args)
    _assert_ids(result, IID1, IID2, IID3, IID4)


def test_keep_with_active():
    images = [
        image_entry(IID1, mins_ago(200), "foo:v1.1"),
        image_entry(IID2, mins_ago(190), "foo:v1.2"),
        image_entry(IID3, mins_ago(180), "foo:v1.3"),
        image_entry(IID4, mins_ago(170), "foo:v1.4", "foo:latest"),
    ]
    containers = [
        created_container_entry(CID1, IID2, mins_ago(5)),
        created_container_entry(CID2, IID3, mins_ago(5))]
    args = parse_arguments(['images', '--keep', '2'])
    result = determine_images_to_remove(images, containers_result(containers), args)
    _assert_ids(result, IID1)


def test_keep_with_active_and_filter():
    images = [
        image_entry(IID1, mins_ago(200), "foo:v1.1"),
        image_entry(IID2, mins_ago(190), "foo:v1.2"),
        image_entry(IID3, mins_ago(180), "foo:v1.3"),
        image_entry(IID4, mins_ago(170), "foo:v1.4", "foo:latest"),
    ]
    containers = [
        created_container_entry(CID1, IID2, mins_ago(5)),
        created_container_entry(CID2, IID3, mins_ago(5))]
    args = parse_arguments(['images', '--keep', '2', '--name', 'foo'])
    result = determine_images_to_remove(images, containers_result(containers), args)
    _assert_ids(result, IID1)


def test_keep_multiname():
    images = [
        image_entry(IID1, mins_ago(200), "foo:v1.1", "bar:v1"),
        image_entry(IID2, mins_ago(190), "foo:v1.2"),
        image_entry(IID3, mins_ago(180), "foo:v1.3"),
        image_entry(IID4, mins_ago(170), "foo:v1.4"),
    ]
    args = parse_arguments(['images', '--keep', '2'])
    result = determine_images_to_remove(images, [], args)
    _assert_ids(result, IID2)


def test_keep_multiname_with_filter():
    """Even though we're only deleting records with name "foo", "keep" trumps filters"""
    images = [
        image_entry(IID1, mins_ago(200), "foo:v1.1", "bar:v1"),
        image_entry(IID2, mins_ago(190), "foo:v1.2"),
        image_entry(IID3, mins_ago(180), "foo:v1.3"),
        image_entry(IID4, mins_ago(170), "foo:v1.4"),
    ]
    args = parse_arguments(['images', '--keep', '2', '--name', 'foo'])
    result = determine_images_to_remove(images, [], args)
    _assert_ids(result, IID2)


def test_negative_tag_filter():
    images = [
        image_entry(IID1, mins_ago(200), "foo:v1.1", "foo:latest"),
        image_entry(IID2, mins_ago(190), "foo:v1.2"),
        image_entry(IID3, mins_ago(180), "foo:v1.3"),
        image_entry(IID4, mins_ago(170), "foo:v1.4"),
    ]
    args = parse_arguments(['images', '--keep', '2', '--tag', '~latest'])
    result = determine_images_to_remove(images, [], args)
    _assert_ids(result, IID2)


def test_negative_tag_on_different_name_filter():
    images = [
        image_entry(IID1, mins_ago(200), "foo:v1.1", "bar:latest"),
        image_entry(IID2, mins_ago(190), "foo:v1.2"),
        image_entry(IID3, mins_ago(180), "foo:v1.3"),
        image_entry(IID4, mins_ago(170), "foo:v1.4"),
    ]
    args = parse_arguments(['images', '--keep', '2', '--tag', '~latest'])
    result = determine_images_to_remove(images, [], args)
    _assert_ids(result, IID2)


def test_positive_name_filter():
    images = [
        image_entry(IID1, mins_ago(200), "somewhere.org/someorg/foo:v1.1"),
        image_entry(IID2, mins_ago(190), "someorg/foo:v1.2"),
        image_entry(IID3, mins_ago(180), "someorg/foo:v1.3"),
        image_entry(IID4, mins_ago(210), "someorg/bar:R1"),
        image_entry(IID4, mins_ago(195), "somewhere.org/someorg/bar:R2"),
        image_entry(IID4, mins_ago(165), "someorg/bar:R3"),
    ]
    args = parse_arguments(['images', '--keep', '2', '--name', 'someorg/foo'])
    result = determine_images_to_remove(images, [], args)
    _assert_ids(result, IID1)


def test_partial_name_doesnt_match():
    images = [
        image_entry(IID1, mins_ago(200), "somewhere.org/someorg/foo:v1.1"),
        image_entry(IID2, mins_ago(190), "someorg/foo:v1.2"),
        image_entry(IID3, mins_ago(180), "someorg/foo:v1.3"),
        image_entry(IID4, mins_ago(210), "someorg/foo_monitor:R1"),
        image_entry(IID4, mins_ago(195), "somewhere.org/someorg/foo_monitor:R2"),
        image_entry(IID4, mins_ago(165), "someorg/foo_monitor:R3"),
    ]
    args = parse_arguments(['images', '--keep', '2', '--name', 'someorg/foo'])
    result = determine_images_to_remove(images, [], args)
    _assert_ids(result, IID1)


def test_regexes():
    images = [
        # should be deleted
        image_entry(IID1, mins_ago(200), "somewhere.org/someorg/foo:v1.1"),
        image_entry(IID2, mins_ago(190), "someorg/foo:v1.2"),
        # should be skipped
        image_entry(IID3, mins_ago(190), "awesomeorg/foo:v1.2"),
        image_entry(IID4, mins_ago(180), "someorg/notfoo:v1.3"),
        image_entry(IID5, mins_ago(180), "someorg/Foo:v1.3"),
        image_entry(IID6, mins_ago(180), "someorg/foo_nope:v1.3"),
        image_entry(IID7, mins_ago(180), "someorg/nope/foo:v1.3"),
    ]
    args = parse_arguments(['images', '--keep', '0', '--name', 'someorg/[^/]*', '--name', '[^/]*/foo'])
    result = determine_images_to_remove(images, [], args)
    _assert_ids(result, IID1, IID2)

