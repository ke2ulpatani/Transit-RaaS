transit_endpt=$1
remote_hyp_ip=$2

ip route add $transit_endpt via $remote_hyp_ip
