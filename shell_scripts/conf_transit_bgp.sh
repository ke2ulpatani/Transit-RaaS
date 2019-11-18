#!/bin/bash

self_as=$1
rip1=$2
ras1=$3
rip2=$4
ras2=$5

setsebool zebra_write_config 1

vtysh -c "conf t" -c "no router bgp 7675" -c "router bgp $self_as" \
	-c "neighbor $rip1 remote-as $ras1" -c "neighbor $rip2 remote-as $ras2" \
	-c "end" -c "write"
