#!/bin/bash
self_as=$1
rip1=$2
ras1=$3
c_name=$4
adv_subnets=$5

#setsebool zebra_write_config 1

echo $c_name $self_as $rip1 $ras1 > bgp_file_new.txt
docker exec -it $c_name vtysh -c "conf t" \#-c "no router bgp 7675" \
	-c "router bgp $self_as" \
	-c "neighbor $rip1 remote-as $ras1" \
	-c "end" -c "write"

for subnet in $(echo $adv_subnets | sed 's/,/ /g'); do
    docker exec -it $c_name vtysh -c "conf t" -c "router bgp $self_as" \
		-c "network $subnet"
done

docker exec -it $c_name vtysh -c "end" -c "write"
