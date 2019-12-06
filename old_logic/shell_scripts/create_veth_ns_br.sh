##./create_veth_ns1_ns2 ns1 ns1_ip ns2 ns2_ip cid

#ns
ns=$1
ns_ip=$2

#bridge
br=$3

#customer id
cid=$4

e1=$cid_$ns_$br
e2=$cid_$br_$ns

ip link add $e1 type veth peer name $e2
ip link set $e1 netns $ns1
brctl addif $br $e2

#configure ip of ns
ip netns exec $ns ip addr add $ns_ip dev $e1
ip netns exec $ns ip link set $e1 up

#configure bridge if
ip link set $e2 up
