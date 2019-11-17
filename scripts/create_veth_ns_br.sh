##./create_veth_ns1_ns2 ns ns_ip br e1 e2

#ns
ns=$1
ns_ip=$2

#bridge
br=$3

#veth pair ids
e1=$4
e2=$5

ip link add $e1 type veth peer name $e2
ip link set $e1 netns $ns
brctl addif $br $e2

#configure ip of ns
ip netns exec $ns ip addr add $ns_ip dev $e1
ip netns exec $ns ip link set $e1 up

#configure bridge if
ip link set $e2 up
