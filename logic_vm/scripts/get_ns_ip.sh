ns_name=$1
ns_if=$2

ip netns exec $ns_name ip -4 addr | grep $ns_if | tail -n 1 | sed 's/\s\+/ /g' | cut -d ' ' -f 3 | cut -d '/' -f 1
