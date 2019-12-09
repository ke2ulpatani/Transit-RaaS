#!/bin/bash

self_as=$1
neighbor_ip=$2
bgp_weight=$3
c_name=$4

#setsebool zebra_write_config 1

docker exec -it $c_name vtysh -c "conf t" -c "no router bgp 7675" -c "router bgp $self_as" \
	-c "neighbor $neighbor_ip weight $bgp_weight" \
	-c "end" -c "write"
