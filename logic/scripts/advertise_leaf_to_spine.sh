#!/bin/bash

spine_self_as=$1
leaf_loopback=$2
c_name=$3


docker exec -it $c_name vtysh -c "conf t" -c "no router bgp 7675" -c "router bgp $spine_self_as" \
-c "network $leaf_loopback" -c "end" -c "write memory"
