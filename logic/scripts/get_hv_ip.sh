if_name=$1

ip -4 addr | grep $if_name | tail -n 1 | sed 's/\s\+/ /g' | cut -d ' ' -f 3
