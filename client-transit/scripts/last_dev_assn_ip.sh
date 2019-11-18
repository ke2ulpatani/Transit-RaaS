#!/bin/bash

ip=$1

intf=$(ip addr | tail -n 4 | head -n 1 | cut -d ' ' -f 2 | cut -d ':' -f 1)
ip link set $intf down
ip addr add $ip dev $intf
ip link set $intf up
