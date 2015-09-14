docker-rotate
=============

In a continuously deployed environment, old and unused docker images accumulate and use up space.
`docker-rotate` helps remove the K oldest images of each type.

[![Build Status](https://travis-ci.org/locationlabs/docker-rotate.png)](https://travis-ci.org/locationlabs/docker-rotate)

Usage:

    # delete all but the three oldest images of each type
    docker-rotate --clean-images --keep 3

    # only target one type of image (by name)
    docker-rotate --clean-images --keep 3 --only organization/image

    # don't actualy delete anything
    docker-rotate --clean-images --keep 3 --dry-run

    # also delete exited containers (except those with volumes)
    docker-rotate --clean-images --clean-containers --keep 3

By default, `docker-rotate` connects to the local Unix socket; the usual environment variables will
be respected if the `--use-env` flag is given.
