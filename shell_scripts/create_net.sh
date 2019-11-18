#!/bin/bash

net_name=$1
br_name=$2

brctl addbr $br_name
ip link set $br_name up

echo "<network>
  <name>$net_name</name>
  <forward mode='bridge'/>
  <bridge name='$br_name'/>
</network>" > /etc/libvirt/qemu/networks/$net_name.xml

virsh net-define /etc/libvirt/qemu/networks/$net_name.xml
virsh net-start $net_name
