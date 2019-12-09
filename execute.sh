#!/bin/bash

cmd=$1
config_file=$2

if [ $cmd == "help" ]; then
	echo help
fi

if [ $cmd == "create_vpc" ]; then
	python3 logic/create_vpc.py $config_file
fi

if [ $cmd == "create_spine" ]; then
	python3 logic/create_spine.py $config_file
fi

if [ $cmd == "create_leaf" ]; then
	python3 logic/create_leaf.py $config_file True
fi

if [ $cmd == "create_pc" ]; then
	python3 logic/create_pc.py $config_file
fi

if [ $cmd == "connect_pc_leaf" ]; then
	python3 logic/connect_pc_leaf.py $config_file
fi

if [ $cmd == "create_l1_transit" ]; then
	python3 logic/create_l1_transit.py $config_file
fi

if [ $cmd == "create_l2_transit" ]; then
	python3 logic/create_l2_transit.py $config_file
fi

if [ $cmd == "connect_s_l1t" ]; then
	python3 logic/connect_s_l1t.py $config_file
fi

if [ $cmd == "connect_l1t_l2t" ]; then
	python3 logic/connect_transit_l1_l2.py $config_file
fi

if [ $cmd == "enable_ecmp" ]; then
	python3 logic/bgp_multipath.py $config_file
fi

if [ $cmd == "connect_leafs_vxlan" ]; then
	python3 logic/connect_leafs_vxlan.py $config_file
fi

if [ $cmd == "influence_path" ]; then
	python3 logic/influence_path.py $config_file
fi
