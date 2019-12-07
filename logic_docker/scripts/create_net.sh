#!/bin/bash

br_name=$1

brctl addbr $br_name
ip link set $br_name up