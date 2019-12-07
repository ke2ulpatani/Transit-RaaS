#!/bin/bash

cmd=$1
config_file=$2


if [ $cmd == "create_vpc" ]; then
	python3 logic/create_vpc.py $config_file
fi

if [ $cmd == "create_spine" ]; then
	python3 logic/create_spine.py $config_file
fi

if [ $cmd == "create_leaf" ]; then
	python3 logic/create_leaf.py $config_file
fi

if [ $cmd == "create_pc" ]; then
	python3 logic/create_pc.py $config_file
fi
