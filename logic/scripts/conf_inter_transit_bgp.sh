#!/bin/bash
self_as=$1
rip1=$2
ras1=$3
bgp_lo=$4
c_name=$5

#setsebool zebra_write_config 1

docker -it exec $cname vtysh -c "conf t" -c "no router bgp 7675" -c "router bgp $self_as" \
	-c "neighbor $rip1 remote-as $ras1"  \
	-c "neighbor $rip1 update-source $bgp_lo" -c "neighbor $rip1 ebgp-multihop 16" -c "end" -c "write"
