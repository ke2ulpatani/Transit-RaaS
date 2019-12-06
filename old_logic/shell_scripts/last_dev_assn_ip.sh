#!/bin/bash

ip=$1

if=$(ip addr | tail -n 2 | head -n 1 | cut -d ' ' -f 2 | cut -d ':' -f 1)
ip link set $if down
ip link add $ip dev $if
ip link set $if up
