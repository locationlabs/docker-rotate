from collections import defaultdict

from docker.errors import APIError

from dockerrotate.filter import include_image


def clean_images(args):
    """
    Delete old images keeping the most recent N images by tag.
    """
    # should not need to inspect all images; only intermediate images should appear
    # when all is true; these should be deleted along with dependent images
    images = [image
              for image in args.client.images(all=False)
              if include_image(image["RepoTags"], args)]

    # index by id
    images_by_id = {
        image["Id"]: image for image in images
    }

    # group by name
    images_by_name = defaultdict(set)
    for image in images:
        for tag in image["RepoTags"]:
            image_name = normalize_tag_name(tag)
            images_by_name[image_name].add(image["Id"])

    for image_name, image_ids in images_by_name.items():
        # sort/keep
        images_to_delete = sorted([
            images_by_id[image_id] for image_id in image_ids],
            key=lambda image: -image["Created"],
        )[args.keep:]

        # delete
        for image in images_to_delete:
            print "Removing image ID: {}, Tags: {}".format(
                image["Id"],
                ", ".join(image["RepoTags"])
            )

            if args.dry_run:
                continue

            try:
                args.client.remove_image(image["Id"], force=True, noprune=False)
            except APIError as error:
                print error.message


def normalize_tag_name(tag):
    """
    docker-py provides image names with tags as a single string.

    We want:

       some.domain.com/organization/image:tag -> organization/image
                       organization/image:tag -> organization/image
                                    image:tag ->              image
    """
    return "/".join(tag.rsplit(":", 1)[0].split("/")[-2:])
