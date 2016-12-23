from dateutil import parser

from docker.errors import APIError


def all_containers(args):
    """
    Return data for all containers.

    Includes backward-compatibility for the ImageID field.
    """
    containers = args.client.containers(all=True)

    if containers and "ImageID" not in containers[0]:
        # pre-1.21 API: retrieve image IDs
        for container in containers:
            container["ImageID"] = args.client.inspect_container(container["Id"])["Image"]

    return containers


def inspect_container(container, args):
    """
    Return inspection data for the given container.

    Includes backward-compatibility for the State.Status field.
    """

    inspect_data = args.client.inspect_container(container["Id"])
    if "Status" not in inspect_data["State"]:
        # pre-1.21 API: synthesize Status from other State fields
        inspect_data["State"]["Status"] = (
            "restarting" if inspect_data["State"]["Restarting"] else
            "running" if inspect_data["State"]["Running"] else
            "paused" if inspect_data["State"]["Paused"] else
            "dead" if inspect_data["State"].get("Dead", False) else
            "exited" if (not inspect_data["State"]["Pid"]
                         and inspect_data["State"]["StartedAt"] >= inspect_data["Created"]) else
            "created"
        )
    return inspect_data


def include_container(container, args):
    """
    Return truthy if container should be removed.
    """
    inspect_data = inspect_container(container, args)
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
        container for container in all_containers(args)
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
