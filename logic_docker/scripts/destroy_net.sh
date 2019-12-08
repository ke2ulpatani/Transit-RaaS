#!/bin/bash

net_name=$1
br_name=$2

ip link set $br_name down
brctl delbr $br_name

virsh net-destroy $net_name
virsh net-undefine $net_name
