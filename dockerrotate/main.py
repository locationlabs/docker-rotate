"""
Free up space by rotating out old Docker images and containers.
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from docker import Client
from docker.errors import NotFound
from docker.utils import kwargs_from_env

from dockerrotate.images import clean_images
from dockerrotate.containers import clean_containers

UNIX_SOC_ARGS = {"base_url": "unix://var/run/docker.sock"}


def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-e", "--use-env",
        action="store_true",
        help="Load docker connection information from standard environment variables.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not remove anything",
    )
    parser.add_argument(
        "--client-version",
        help="Specify client version to use.",
    )

    subparsers = parser.add_subparsers()

    images_parser = subparsers.add_parser(
        "images",
        help="Clean out old images",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    images_parser.set_defaults(cmd=clean_images)
    images_parser.add_argument(
        "--keep",
        "-k",
        type=int,
        default=3,
        help="Keep this many images of each kind",
    )
    images_parser.add_argument(
        "--images",
        nargs='*',
        help="Python regex of image names to remove. Use a '~' prefix for negative match.",
    )

    containers_parser = subparsers.add_parser(
        "containers",
        help="Clean out old containers",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    containers_parser.set_defaults(cmd=clean_containers)
    containers_parser.add_argument(
        "--exited",
        default="1h",
        help="Remove only containers that exited that long ago",
    )
    containers_parser.add_argument(
        "--created",
        default="1d",
        help="Remove only containers that where created (but not running) that long ago",
    )
    containers_parser.add_argument(
        "--images",
        nargs='*',
        help="Python regex of image names to remove. Use a '~' prefix for negative match.",
    )

    return parser.parse_args()


def make_client(args):
    """
    Create a Docker client.

    Either use the local socket (default) or use the standard environment
    variables (e.g. DOCKER_HOST). This is much simpler than trying to pass
    all the possible certificate options through argparse.
    """
    kwargs = kwargs_from_env(assert_hostname=False) if args.use_env else UNIX_SOC_ARGS

    if args.client_version:
        kwargs["version"] = args.client_version

    client = Client(**kwargs)

    # Verify client can talk to server.
    try:
        client.version()
    except NotFound as error:
        raise SystemExit(error)

    return client


def main():
    """
    CLI entry point.
    """
    args = parse_args()
    args.client = make_client(args)

    args.cmd(args)
