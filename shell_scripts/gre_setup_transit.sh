#!/bin/bash


neigh_bgp_lo_ip=$1
gre_tun_name=$2
local_ip=$3
remote_ip=$4

ip tunnel add $gre_tun_name mode gre local $local_ip remote $remote_ip
ip link set $gre_tun_name up
ip route add $neigh_bgp_lo_ip dev $gre_tun_name
