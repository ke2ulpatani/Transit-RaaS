#!/bin/bash

cmd=$1
config_file=$2

if [ $cmd == "help" ]; then
	echo help
fi

if [ $cmd == "create_vpc" ]; then
    echo "VPC creation started" >> client.log
	python3 logic/create_vpc.py $config_file
fi

if [ $cmd == "create_spine" ]; then
    echo "Spine creation started" >> client.log
	python3 logic/create_spine.py $config_file
fi

if [ $cmd == "create_leaf" ]; then
    echo "Leaf creation started" >> client.log
	python3 logic/create_leaf.py $config_file True
fi

if [ $cmd == "create_dummy_leaf" ]; then
    echo "Leaf creation started" >> client.log
    python3 logic/create_leaf.py $config_file False
fi

if [ $cmd == "create_pc" ]; then
    echo "VM creation started" >> client.log
	python3 logic/create_pc.py $config_file
fi

if [ $cmd == "connect_pc_leaf" ]; then
    echo "Connecting PC to subnet started" >> client.log
	python3 logic/connect_pc_leaf.py $config_file
fi

if [ $cmd == "create_l1_transit" ]; then
    echo "L1 transit creation started" >> client.log
	python3 logic/create_l1_transit.py $config_file
fi

if [ $cmd == "create_l2_transit" ]; then
    echo "L2 transit creation started" >> client.log
	python3 logic/create_l2_transit.py $config_file
fi

if [ $cmd == "connect_s_l1t" ]; then
    echo "Connection to spine to l1 started" >> client.log
	python3 logic/connect_s_l1t.py $config_file
fi

if [ $cmd == "connect_l1t_l2t" ]; then
    echo "Connection to l1 to l2 set up started" >> client.log
	python3 logic/connect_transit_l1_l2.py $config_file
fi

if [ $cmd == "enable_ecmp" ]; then
    echo "ECMP requestion started" >> client.log
	python3 logic/bgp_multipath.py $config_file
fi

if [ $cmd == "connect_leafs_vxlan" ]; then
	python3 logic/connect_leafs_vxlan.py $config_file
fi

if [ $cmd == "influence_path" ]; then
    echo "Influence path started" >> client.log
	python3 logic/influence_path.py $config_file
	echo hhi
fi

if [ $cmd == "checkpoint_restore" ]; then
    echo "Checkpoint started" >> client.log
	python3 logic/checkpoint_restore.py $1 $2
fi

if [ $cmd == "conf_spine_bgp" ]; then
        python3 logic/conf_spine_bgp.py $conf_file
fi

