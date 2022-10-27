"""
Code to handle the removal of untagged images. While it's possible to handle untagged image
cleanup with command line utilities alone, using something like:

   docker images -f dangling=true -q | xargs docker rmi

... it also makes sense to consolidate cleanup in a single tool. (I note that, in the case
where an untagged image is in use, the above will generate an error message, whereas the code
here is smart enough not to try to delete images that are in use.)
"""
from docker.errors import APIError

from dockerrotate.containers import all_containers


def _find_image_ids_in_use(containers):
    return set(container["ImageID"] for container in containers)


def clean_untagged(args):
    containers = all_containers(args)
    untagged_images = args.client.images(filters=dict(dangling=True))
    image_ids_in_use = _find_image_ids_in_use(containers)

    for image in untagged_images:
        if image["Id"] in image_ids_in_use:
            continue

        print "Removing untagged image with Id: {}".format(image["Id"])

        if args.dry_run:
            continue

        try:
            args.client.remove_image(image["Id"], noprune=False)
        except APIError as error:
            print "unexpected: API error while trying to delete untagged image. Error message is:"
            print error.message
