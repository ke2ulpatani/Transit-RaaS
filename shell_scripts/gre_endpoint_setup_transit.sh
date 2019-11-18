transit_endpt=$1
outip=$2

ip route add $transit_endpt via $2
