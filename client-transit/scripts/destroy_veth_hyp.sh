veth_name=$1
ip link set $veth_name down
ip link del $veth_name type veth
