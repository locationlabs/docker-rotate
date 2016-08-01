from dateutil import parser

from docker.errors import APIError


def include_container(container, args):
    """
    Return truthy if container should be removed.
    """
    inspect_data = args.client.inspect_container(container["Id"])
    status = inspect_data["State"]["Status"]

    # Note that while a timedelta of zero is a valid value for the created/exited/dead fields,
    # it evaluates to False; hence the "is not None" clauses below.
    if status == "exited" and args.exited is not None:
        finished_at = parser.parse(inspect_data["State"]["FinishedAt"])
        if (args.now - finished_at) < args.exited:
            return False
    elif status == "created" and args.created is not None:
        created_at = parser.parse(inspect_data["Created"])
        if (args.now - created_at) < args.created:
            return False
    elif status == "dead" and args.dead is not None:
        finished_at = parser.parse(inspect_data["State"]["FinishedAt"])
        if (args.now - finished_at) < args.dead:
            return False
    else:
        return False

    return True


def determine_containers_to_remove(args):
    return [
        container for container in args.client.containers(all=True)
        if include_container(container, args)
    ]


def clean_containers(args):
    """
    Delete non-running containers.

    Images cannot be deleted if in use. Deleting dead containers allows
    more images to be cleaned.
    """

    for container in determine_containers_to_remove(args):
        print "Removing container ID: {}, Name: {}, Image: {}".format(
            container["Id"],
            (container.get("Names") or ["N/A"])[0],
            container["Image"],
        )

        if args.dry_run:
            continue

        try:
            args.client.remove_container(container["Id"])
        except APIError as error:
            print "Unable to remove container: {}: {}".format(
                container["Id"],
                error,
            )
