#!/bin/bash

self_as=$1
activate=$2
c_name=$3

#setsebool zebra_write_config 1

if [ $activate == "true" ]
then
    docker exec -it $c_name vtysh -c "conf t" -c "no router bgp 7675" -c "router bgp $self_as" \
	-c "maximum-paths 8" \
	-c "end" -c "write"
else
    docker exec -it $c_name vtysh -c "conf t" -c "no router bgp 7675" -c "router bgp $self_as" \
	-c "maximum-paths 1" \
	-c "end" -c "write"
fi