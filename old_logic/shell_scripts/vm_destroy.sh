#!/bin/bash

vm=$1
sudo virsh destroy $vm
sudo virsh undefine $vm --remove-all-storage
