#!/bin/bash

self_as=$1
c_name=$2

#setsebool zebra_write_config 1

docker exec -it $c_name vtysh -c "conf t" -c "no router bgp 7675" -c "router bgp $self_as" \
	-c "maximum-paths 8" \
	-c "end" -c "write"


