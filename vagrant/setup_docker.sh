#!/bin/bash

# Sets up Docker on a normal Ubuntu 14.04 host, based on the first command-line argument, which
# specifies the Docker version

# Make the HTTPS transport is available to APT
if [ ! -e /usr/lib/apt/methods/https ]; then
    apt-get update
    apt-get install -y apt-transport-https
fi

DOCKER_VERSION=$1

if [ "$DOCKER_VERSION" == "1.5.0" ] ; then
   DOCKER_PACKAGE="lxc-docker-1.5.0"

   apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9

   echo deb https://get.docker.com/ubuntu docker main > /etc/apt/sources.list.d/docker.list
else
   DOCKER_PACKAGE="docker-engine=${DOCKER_VERSION}-0~trusty"

   apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D

   echo deb https://apt.dockerproject.org/repo ubuntu-trusty main > /etc/apt/sources.list.d/docker.list
fi

# Install docker and python
apt-get update
apt-get install -y $DOCKER_PACKAGE python-pip
pip install --upgrade virtualenv tox pip
adduser vagrant docker
