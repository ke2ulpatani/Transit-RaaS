##./create_veth_ns1_ns2 ns1 ns1_ip ns2 ns2_ip cid

#ns1
ns1=$1
ns1_ip=$2


#ns2
ns2=$3
ns2_ip=$4

#customer id
cid=$5

e1=$cid_$ns1_$ns2
e2=$cid_$ns2_$ns1

ip link add $e1 type veth peer name $e2
ip link set $e1 netns $ns1
ip link set $e2 netns $ns2

#configure ip of ns1
ip netns exec $ns1 ip link add $ns1_ip dev $e1
ip netns exec $ns1 ip link set $e1 up

#configure ip of ns2
ip netns exec $ns2 ip link add $ns2_ip dev $e2
ip netns exec $ns2 ip link set $e2 up
