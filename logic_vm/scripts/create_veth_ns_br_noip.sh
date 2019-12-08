##./create_veth_ns1_ns2 ns ns_ip br e1 e2

#ns
ns=$1

#bridge
br=$2

#veth pair ids
e1=$3
e2=$4

ip link add $e1 type veth peer name $e2
ip link set $e1 netns $ns
brctl addif $br $e2

#configure nets interface to be up
ip netns exec $ns ip link set $e1 up

#configure bridge if
ip link set $e2 up
