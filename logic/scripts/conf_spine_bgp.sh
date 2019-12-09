#!/bin/bash
self_as=$1
rip1=$2
ras1=$3
adv_subnets=$4
c_name=$5

#setsebool zebra_write_config 1

docker -it exec $c_name vtysh -c "conf t" -c "no router bgp 7675" -c "router bgp $self_as" \
	-c "neighbor $rip1 remote-as $ras1" \
	-c "end" -c "write"

for i in $(echo $adv_subnets | sed 's/,/ /g'); do
    docker -it exec $c_name vtysh -c "conf t" -c "router bgp $self_as" \
		-c "network $subnet"
done

docker -it exec $c_name vtysh -c "end" -c "write"
