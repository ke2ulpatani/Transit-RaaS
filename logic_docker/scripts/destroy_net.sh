#!/bin/bash

br_name=$1

ip link set $br_name down
brctl delbr $br_name
