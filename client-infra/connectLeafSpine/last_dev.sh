#!/bin/bash

ipp=$1
ad_ip=$2
next_hop=$3

iff=$(ip addr | tail -n 4 | head -n 1 | cut -d ' ' -f 2 | cut -d ':' -f 1)
ip link set $iff down
ip addr add $ipp dev $iff
ip link set $iff up

ip route add $ad_ip via $next_hop
