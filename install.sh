#!/bin/bash
DIR=endangered_venv

sudo pip install --upgrade virtualenv

if [ ! -d $DIR ]
then
	virtualenv endangered_venv
fi

. ./endangered_venv/bin/activate
pip install --upgrade opencv-python
pip install --upgrade numba
pip install --upgrade imageio
pip install --upgrade numpy
