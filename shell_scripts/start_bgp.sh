#!/bin/bash

cp /usr/share/doc/quagga-*/bgpd.conf.sample /etc/quagga/bgpd.conf
systemctl start bgpd
systemctl enable bgpd
