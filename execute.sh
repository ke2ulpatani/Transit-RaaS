#!/bin/bash

cmd=$1
config_file=$2


if [ $cmd == "create_vpc" ]; then
	python3 logic/create_vpc.py $config_file
fi
