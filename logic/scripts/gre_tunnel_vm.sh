#!/bin/bash

#./gre_tunnel_vm add gretunnelname local_ip remote_ip remote_subnet

#Default mode "gre"
mode="gre"

#add or delete tunnel
action=$1

#name of tunnel
name=$2

#Name of namespaces as endpoints and corresponding ip addresses with VM subnets
#Refer readme for topology

local_ip=$3
remote_ip=$4
remote_subnet=$5


if [ $action = "add" ]; then
	#at ns1
	sudo ip tunnel add $name mode $mode local $local_ip remote $remote_ip
	sudo ip link set dev $name up
	sudo ip route add $remote_subnet dev $name

elif [ $action = "del" ]; then
	sudo ip tunnel del $name mode $mode local $local_ip remote $remote_ip
fi
