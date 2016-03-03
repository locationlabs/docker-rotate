docker-rotate
=============

In a continuously deployed environment, old and unused docker images and containers accumulate and use up space.
`docker-rotate` helps remove the K oldest images of each type and remove non-running containers.

[![Build Status](https://travis-ci.org/locationlabs/docker-rotate.png)](https://travis-ci.org/locationlabs/docker-rotate)

Usage:

    # delete all but the three oldest images of each type
    docker-rotate images --keep 3

    # only target one type of image but don't remove latest
    docker-rotate images --keep 3 --image "organization/image" "~:latest"

    # don't actualy delete anything
    docker-rotate --dry-run images --keep 3

    # delete containers exited more than an hour ago
    docker-rotate containers --exited 1h

By default, `docker-rotate` connects to the local Unix socket; the usual environment variables will
be respected if the `--use-env` flag is given.
