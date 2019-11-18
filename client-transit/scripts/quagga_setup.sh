setsebool zebra_write_config 1
cp /etc/quagga/zebra.conf /etc/quagga/zebra.conf.old
cp /usr/share/doc/quagga-*/zebra.conf.sample /etc/quagga/zebra.conf
systemctl start zebra
systemctl enable zebra


cp /usr/share/doc/quagga-*/bgpd.conf.sample /etc/quagga/bgpd.conf
systemctl start bgpd
systemctl enable bgpd

chmod -R 777 /etc/quagga/

sysctl net.ipv4.ip_forward=1

iptables -F

