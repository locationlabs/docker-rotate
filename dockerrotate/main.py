"""
Free up space by rotating out old Docker images.
"""
from argparse import ArgumentParser
from datetime import timedelta

from dateutil import parser
from docker import Client
from docker.errors import APIError
from docker.utils import kwargs_from_env


TEN_SECONDS = timedelta(seconds=10)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--use-env",
        "-e",
        action="store_true",
        help="Load docker connection information from standard environment variables.",
    )
    parser.add_argument(
        "--clean-containers",
        "-c",
        action="store_true",
        help="Clean out old containers",
    )
    parser.add_argument(
        "--clean-images",
        "-i",
        action="store_true",
        help="Clean out old images",
    )
    parser.add_argument(
        "--keep",
        "-k",
        type=int,
        default=3,
        help="Keep this many images of each kind",
    )
    parser.add_argument(
        "--only",
        "-o",
        help="Only process this image",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not remove anything",
    )
    return parser.parse_args()


def make_client(args):
    """
    Create a Docker client.

    Either use the local socket (default) or use the standard environment
    variables (e.g. DOCKER_HOST). This is much simpler than trying to pass
    all the possible certificate options through argparse.
    """
    if args.use_env:
        return Client(**kwargs_from_env(assert_hostname=False))
    else:
        return Client(base_url='unix://var/run/docker.sock')


def normalize_tag_name(tag):
    """
    docker-py provides image names as a single string.

    We want:

       some.domain.com/organization/image:tag -> organization/image
                       organization/image:tag -> organization/image
                                    image:tag ->              image
    """
    return "/".join(tag.rsplit(":", 1)[0].split("/")[-2:])


def might_be_data_volume(client, container):
    """
    Data volumes are non-running containers that we do not want to delete.

    Detecting a data volume doesn't apear to be an exact science, but we
    can use some of the information from `docker inspect` to make a good
    guess.
    """
    inspect_data = client.inspect_container(container["Id"])
    if not inspect_data["Config"]["Volumes"]:
        # data volumes should have volumes...
        return False
    if inspect_data["State"]["ExitCode"] != 0:
        # data volumes need to have exited cleanly
        return False
    started_at = parser.parse(inspect_data["State"]["StartedAt"])
    finished_at = parser.parse(inspect_data["State"]["FinishedAt"])
    if finished_at < started_at:
        # not actually finished
        return False
    if (finished_at - started_at) > TEN_SECONDS:
        # data volumes should terminate quickly
        return False
    # probably a data volume
    return True


def clean_containers(client, args):
    """
    Delete non-running containers.

    Skips over containers with volumes.

    Images cannot be deleted if in use. Deleting dead containers allows
    more images to be cleaned.
    """
    running_containers = {
        container["Id"] for container in client.containers()
    }
    stopped_containers = [
        container for container in client.containers(all=True)
        if container["Id"] not in running_containers
    ]
    for container in stopped_containers:
        image_name = normalize_tag_name(container["Image"])
        if args.only and args.only != image_name:
            continue
        if might_be_data_volume(client, container):
            print "Skipping data volume: {}".format(container["Names"][0])
            continue
        print "Removing container ID: {}, Name: {}, Image: {}".format(
            container["Id"],
            container["Names"][0],
            image_name
        )
        if args.dry_run:
            continue
        client.remove_container(container["Id"])


def clean_images(client, args):
    """
    Delete old images keeping the most recent N images by tag.
    """
    # should not need to inspect all images; only intermediate images should appear
    # when all is true; these should be deleted along with dependent images
    images = client.images(all=False)

    # index by id
    images_by_id = {
        image["Id"]: image for image in images
    }

    # group by name
    images_by_name = {}
    for image in images:
        for tag in image["RepoTags"]:
            image_name = normalize_tag_name(tag)
            if args.only and args.only != image_name:
                continue
            images_by_name.setdefault(image_name, set()).add(image["Id"])

    for image_name, image_ids in images_by_name.items():
        # sort/keep
        images = sorted([
            images_by_id[image_id] for image_id in image_ids],
            key=lambda image: -image["Created"],
        )
        images_to_delete = images[args.keep:]

        # delete
        for image in images_to_delete:
            print "Removing image ID: {}, Tags: {}".format(
                image["Id"],
                ", ".join(image["RepoTags"])
            )
            if args.dry_run:
                continue
            # In some scenarios, deleting an image with mutiple tags only removes one tag at a time
            # (and all tags must be removed in order to fully delete the image).
            # More investigation needed.
            for tag in image["RepoTags"]:
                try:
                    client.remove_image(image["Id"], force=True, noprune=False)
                except APIError as error:
                    print error.message


def main():
    """
    CLI entry point.
    """
    args = parse_args()
    client = make_client(args)

    if args.clean_containers:
        clean_containers(client, args)

    if args.clean_images:
        clean_images(client, args)
