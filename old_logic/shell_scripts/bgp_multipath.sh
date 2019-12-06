#!/bin/bash

self_as=$1

setsebool zebra_write_config 1

vtysh -c "conf t" -c "no router bgp 7675" -c "router bgp $self_as" \
	-c "maximum-paths 8" \
	-c "end" -c "write"


