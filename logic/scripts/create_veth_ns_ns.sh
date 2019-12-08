#!/bin/bash

ns1=$1
ns1_ip=$2
ns1_veth=$3

ns2=$4
ns2_ip=$5
ns2_veth=$6


ip link add $ns1_veth type veth peer name $ns2_veth
ip link set $ns1_veth netns $ns1
ip link set $ns2_veth netns $ns2
ip netns exec $ns1 ip addr add $ns1_ip dev $ns1_veth
ip netns exec $ns1 ip link set $ns1_veth up
ip netns exec $ns2 ip addr add $ns2_ip dev $ns2_veth
ip netns exec $ns2 ip link set $ns2_veth up