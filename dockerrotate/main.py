"""
Free up space by rotating out old Docker images and containers.
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, ArgumentTypeError
from datetime import datetime, timedelta
import re

from dateutil.tz import tzutc
from docker import Client
from docker.errors import NotFound
from docker.utils import kwargs_from_env

from dockerrotate.containers import clean_containers
from dockerrotate.images import clean_images
from dockerrotate.untagged import clean_untagged


UNIX_SOC_ARGS = {"base_url": "unix://var/run/docker.sock"}

TIME_REGEX = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')  # noqa


def time_delta_type(time_str):
    """
    Parse a human readable time delta string into a timedelta object
    """
    parts = TIME_REGEX.match(time_str)
    if not parts:
        raise ArgumentTypeError("Invalid time delta format '{}'".format(time_str))
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.iteritems():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def argument_parser():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not remove anything",
    )
    parser.add_argument(
        "--client-version",
        help="Specify client version to use.",
    )

    subparsers = parser.add_subparsers(title="Subcommands")

    images_parser = subparsers.add_parser(
        "images",
        help="Clean up old tagged images",
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog="Multiple \"--name\" and \"--tag\" arguments can be provided. Only images that "
               "match ALL of the supplied expressions will be considered for cleanup."
    )
    images_parser.set_defaults(func=clean_images)
    images_parser.add_argument(
        "--keep",
        "-k",
        type=int,
        required=True,
        help="For each image name, keep this many images",
    )

    images_parser.add_argument(
        "--name",
        action="append",
        default=[],
        help="Limit cleanup to images whose name fully matches this (python) regular expression. "
             "Use a '~' prefix to invert matching.",
    )
    images_parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Limit cleanup to images whose tag fully matches this (python) regular expression. "
             "Use a '~' prefix to invert matching.",
    )

    untagged_parser = subparsers.add_parser(
        "untagged-images",
        help="Clean out old untagged images",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    untagged_parser.set_defaults(func=clean_untagged)

    containers_parser = subparsers.add_parser(
        "containers",
        help="Clean out old containers",
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog="The \"exited\", \"created\", and \"dead\" arguments all "
    )
    containers_parser.set_defaults(func=clean_containers)
    containers_parser.add_argument(
        "--exited",
        type=time_delta_type,
        help="Remove \"exited\" containers that finished at least this long ago",
    )
    containers_parser.add_argument(
        "--created",
        type=time_delta_type,
        help="Remove \"created\" containers that were created at least this long ago",
    )
    containers_parser.add_argument(
        "--dead",
        type=time_delta_type,
        help="Remove \"dead\" containers that finished at least this long ago",
    )

    return parser


def parse_arguments(arg_values):
    parser = argument_parser()
    args = parser.parse_args(arg_values)
    args.now = datetime.now(tzutc())
    return args


def make_client(args):
    """
    Create a Docker client.

    Either use the local socket (default) or use the standard environment
    variables (e.g. DOCKER_HOST). This is much simpler than trying to pass
    all the possible certificate options through argparse.
    """
    kwargs = kwargs_from_env(assert_hostname=False)

    if args.client_version:
        kwargs["version"] = args.client_version

    client = Client(**kwargs)

    # Verify client can talk to server.
    try:
        client.version()
    except NotFound as error:
        raise SystemExit(error)

    return client


def main(arg_values=None):
    """
    CLI entry point.
    Allow arg values to be passed in for testing reasons.
    """
    args = parse_arguments(arg_values)

    args.client = make_client(args)

    args.func(args)
