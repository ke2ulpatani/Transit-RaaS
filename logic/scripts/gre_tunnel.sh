#!/bin/bash

#Default mode "gre"
mode="gre"

#add or delete tunnel
action=$1

#name of tunnel
name=$2

#Name of namespaces as endpoints and corresponding ip addresses with VM subnets
#Refer readme for topology
ns1=$3
ns1_ip=$4
ns1_vm_subnet=$5

ns2=$6
ns2_ip=$7
ns2_vm_subnet=$8

if [ $action = "add" ]; then
	#at ns1
	sudo ip netns exec $ns1 ip tunnel add $name mode $mode local $ns1_ip remote $ns2_ip
	sudo ip netns exec $ns1 ip link set dev $name up
	sudo ip netns exec $ns1 ip route add $ns2_vm_subnet dev $name

	#at ns2
	sudo ip netns exec $ns2 ip tunnel add $name mode $mode local $ns2_ip remote $ns1_ip
	sudo ip netns exec $ns2 ip link set dev $name up
	sudo ip netns exec $ns2 ip route add $ns1_vm_subnet dev $name
elif [ $action = "del" ]; then
	sudo ip netns exec $ns1 ip tunnel del $name mode $mode local $ns1_ip remote $ns2_ip
	sudo ip netns exec $ns2 ip tunnel del $name mode $mode local $ns2_ip remote $ns1_ip
fi
