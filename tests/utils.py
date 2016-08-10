"""
This file contains utility classes and generators for use in tests.
"""

import datetime

from dateutil.tz import tzutc

NOW = datetime.datetime.now(tzutc())


def mins_ago(minutes_ago):
    return NOW - datetime.timedelta(minutes=minutes_ago)


def _to_unixtime(dt):
    return int(dt.strftime("%s"))


def _to_timestamp(dt):
    # should only be using this with UTC datetimes
    assert dt.tzinfo == tzutc()
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def image_entry(image_id, created, *repotags):
    return dict(Id=image_id,
                Created=_to_unixtime(created),
                RepoTags=repotags)


def exited_container_entry(container_id, image_id, timestamp):
    return dict(Id=container_id,
                Image=image_id,
                State=dict(ExitCode=0,
                           FinishedAt=_to_timestamp(timestamp),
                           OOMKilled=False,
                           Dead=False,
                           Paused=False,
                           Restarting=False,
                           Running=False,
                           Status="exited"))


def created_container_entry(container_id, image_id, timestamp):
    return dict(
        Id=container_id,
        Image=image_id,
        Created=_to_timestamp(timestamp),
        State=dict(OOMKilled=False,
                   Dead=False,
                   Paused=False,
                   Restarting=False,
                   Running=False,
                   StartedAt=_to_timestamp(timestamp),
                   Status="created"))


def dead_container_entry(container_id, image_id, timestamp):
    return dict(
        Id=container_id,
        Image=image_id,
        State=dict(OOMKilled=False,
                   Dead=True,
                   Paused=False,
                   Restarting=False,
                   Running=False,
                   FinishedAt=_to_timestamp(timestamp),
                   Status="dead"))


def running_container_entry(container_id, image_id, timestamp):
    return dict(
        Id=container_id,
        Image=image_id,
        Created=_to_timestamp(timestamp),
        State=dict(OOMKilled=False,
                   Dead=False,
                   Paused=False,
                   Restarting=False,
                   Running=True,
                   StartedAt=_to_timestamp(timestamp),
                   Status="running"))


def containers_result(containers):
    """
    Generates something that looks like of the result from the "docker.Client.containers()" call.
    Unlike "docker.Client.images()", the result from "container()" is just a stub; full
    information requires a call to "docker.Client.inspect_container()"
    """
    return [dict(Id=container["Id"],
                 ImageID=container["Image"]) for container in containers]


