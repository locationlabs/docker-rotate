#  docker-rotate

In a continuously deployed environment, old and unused docker images and containers accumulate and
use up space. `docker-rotate` provides a way to remove that cruft based on a policy you specify.

[![Build Status](https://travis-ci.org/locationlabs/docker-rotate.png)](https://travis-ci.org/locationlabs/docker-rotate)

## The problem

On a system that is using Docker in a production environment, there are a number of different types
of data that can accumulate over time. They are:
 - old versions of images: if you pull a new version of an image in order to recreate a container,
   the old version can stick around. Depending on how tags are managed in your environment, these
   might have one or more tags, or they might be completely untagged. (For example, if you have
   a image with just the "foo:latest" tag on your system and you run `docker pull foo:latest` to get
   an updated version, the new image will have the "foo:latest" tag and the old image will remain,
   but will now be nameless. If the old image had instead started with "foo:latest" and "foo:xyz",
   it would now be called "foo:xyz")
 - "exited" containers: If a container runs and halts for some reason, and it was not run with the
   `--rm` flag, that container will stay on the system until removed, with the status "exited".
 - "created" containers: If a container is created, e.g. via "docker create", and is never started,
   it will stay on the system until removed. Note that this is sometimes the desired behavior; the
   "docker data container" pattern, as described in
   [the Docker documentation](https://docs.docker.com/engine/tutorials/dockervolumes/#/creating-and-mounting-a-data-volume-container),
   relies on containers remaining in the "created" state indefinitely. This pattern was the standard
   way to share persistent data between container until the `docker volume` API was introduced in
   Docker 1.9

## Usage
This library provides a single command-line tool `docker-rotate` that supports three subcommands:
 - `docker-rotate images` - clean up tagged images
 - `docker-rotate untagged-images` - clean up untagged images
 - `docker-rotate containers` - clean up containers

`docker-rotate` respects the usual DOCKER_* environment variables when connecting to the Docker
engine. For documentation on those, see:
https://docs.docker.com/engine/reference/commandline/cli/#/environment-variables

### docker-rotate images
`docker-rotate images` operates on only tagged images. For each image, it determines an image name
based on the tag, and considers images with the same name together. (For example, images with tags
"registry.somewhere.com/organization/somename:latest", "organization/somename:3.5", and "organization/somename:old_version" are all considered to
have the name "organization/somename".)

`docker-rotate images` will never remove an image associated with a container, regardless of the state
of that container. For that reason, if you plan to clean up containers and images, it's a good idea
to clean up containers first.

Usage examples:

    # clean up all tagged images, retaining the three most recent images for each image name.
    docker-rotate images --keep 3

    # clean up only images matching the specified name, keeping the most recent three
    docker-rotate images --keep 3 --name "organization/name"

    # clean up all images whose tags don't end with ":latest"
    docker-rotate images --keep 0 --tag "~latest"

    # clean up only images from the specified organization, never removing those with the "latest" tag.
    docker-rotate images --keep 3 --name "organization/.*" --tag "~latest"

### docker-rotate untagged-images
`docker-rotate untagged-images` simply removes all images without tags, except images that are in
use by containers. (Again, that means it's a good idea to clean up containers first.)

Usage examples:

    # clean up untagged images
    docker-rotate untagged-images

### docker-rotate containers
`docker-rotate containers` cleans up containers according to the arguments you specify. (For
containers with volumes, those volumes will not be removed.)

Usage examples:

    # clean up all "exited" containers that stopped at least one hour ago
    docker-rotate container --exited 1h

    # clean up all "created" containers that were created at least one day ago
    docker-rotate containers --created 1d

    # clean up all "dead" containers that stopped at least 10 minutes ago
    docker-rotate containers --dead 10m

    # clean up containers in multiple states at once
    docker-rotate container --exited 1h --created 7d --dead 0

