"""
Code to manage the cleanup of images with one or more tags.

The logic here is:
 - identify all images we should retain based on the "keep" argument
 - also identify all images that are in use
 - then, find all images that match our filters and aren't in the first two sets

Evaluation of "keep" is done on a global basis to avoid situations like this:
 - image A has repotags "foo:image1" and "bar:image1", and timestamp N
 - image B has repotag "foo:image2", and timestamp >N
 - the command is run with "--keep 1 --name foo"

... the situation is a bit ambiguous, but an approach that errs on the side of not deleting
things is best.

We *could* also skip the "identify images in use" check, just attempt to delete all of the images,
and rely on Docker blocking the deletion of images that are being used by containers. While that
would simplify the code and might improve runtime a hair, then the tool would generate error output
even when functioning as intended - not a good practice for a tool, as that makes it difficult to
detect real errors.
"""
from collections import defaultdict

from docker.errors import APIError

from dockerrotate.containers import all_containers
from dockerrotate.filter import regex_positive_match, regex_negative_match


def determine_images_to_remove(images, containers, args):
    # Accept images and containers as inputs to make this easier to test

    # see docstring for explanation of what's going on here.
    image_ids_to_keep = find_image_ids_to_keep(images, args)
    image_ids_in_use = _find_image_ids_in_use(containers)

    def matches_filters(image):
        # Images can have multiple names. Allow deletion if:
        #  - ANY of the names matches all of the positive expressions
        #  - ALL of the names pass (i.e don't match ALL of the negative expressions

        def positive_check(name, tag):
            # return true if the name and tag are accepted by all positive regexes
            return (all(regex_positive_match(name_pattern, name) for name_pattern in args.name) and
                    all(regex_positive_match(tag_pattern, tag) for tag_pattern in args.tag))

        def negative_check(name, tag):
            # return true if the name and tag aren't rejected by any of the negative regexes
            return (all(regex_negative_match(name_pattern, name) for name_pattern in args.name) and
                    all(regex_negative_match(tag_pattern, tag) for tag_pattern in args.tag))

        name_tags = [(normalize_tag_name(name_tag), tag_value(name_tag))
                     for name_tag in image["RepoTags"]]

        return any(positive_check(name, tag) for name, tag in name_tags) and \
            all(negative_check(name, tag) for name, tag in name_tags)

    return [image for image in images
            if image["Id"] not in image_ids_to_keep and
            image["Id"] not in image_ids_in_use and
            matches_filters(image)]


def find_image_ids_to_keep(images, args):
    number_to_keep = args.keep

    # Need a special case for keep = 0; below, we use a [-number:] range on a list to
    # pick out the items to keep, and that doesn't work with a zero, because -0 == 0.
    # Luckily, the zero case is easy to calculate..
    if number_to_keep == 0:
        return set()

    images_by_name = defaultdict(list)
    for image in images:
        # each RepoTag produces a name; these are usually the same but can be different.
        image_names = set(normalize_tag_name(name_tag) for name_tag in image["RepoTags"])
        for image_name in image_names:
            images_by_name[image_name].append(image)

    all_ids_to_keep = set()
    for image_name, images_with_name in images_by_name.items():
        images_to_keep = sorted(images_with_name,
                                key=lambda image: image["Created"])[-number_to_keep:]
        all_ids_to_keep.update(image["Id"] for image in images_to_keep)

    return all_ids_to_keep


def _find_image_ids_in_use(containers):
    return set(container["ImageID"] for container in containers)


def clean_images(args):
    """
    Main entry point - delete old images keeping the most recent N images by tag.
    """

    # should not need to inspect all images; only intermediate images should appear
    # when all is true; these should be deleted along with dependent images
    images = args.client.images(all=False)
    containers = all_containers(args)

    images_to_remove = determine_images_to_remove(images, containers, args)

    for image in images_to_remove:
        print "Removing image ID: {}, Tags: {}".format(
            image["Id"],
            ", ".join(image["RepoTags"])
        )

        if args.dry_run:
            continue

        try:
            # The simplest way to do this would be to delete by ID. However, then we
            # encounter issues in the case where we have an image A that is tagged for
            # removal, but that image is a parent image for image B. The desired behavior
            # in that case is that all tags are removed for that image, but the image
            # itself remains until B is removed.
            #
            # force=true is required here because the image we remove might be "latest".

            for repo_tag in image["RepoTags"]:
                args.client.remove_image(repo_tag, force=True, noprune=False)
            else:
                # If the image has no tags (unexpected), fall back to ID.
                args.client.remove_image(image["Id"], force=True, noprune=False)
        except APIError as error:
            print "unexpected: API error while trying to delete image. Error message is:"
            print error.message


def normalize_tag_name(name_tag):
    """
    docker-py provides "RepoTags", which are strings of format "<image name>:<image tag>"

    We want to strip off the tag part and normalize the name:

       some.domain.com/organization/image:tag -> organization/image
                       organization/image:tag -> organization/image
                                    image:tag ->              image
    """
    return "/".join(name_tag.rsplit(":", 1)[0].split("/")[-2:])


def tag_value(name_tag):
    """
    docker-py provides "RepoTags", which are strings of format "<image name>:<image tag>"

    We want just the part after the colon.
    """
    return name_tag.rsplit(":", 1)[1]
