#!/bin/bash

cp /etc/quagga/bgpd.conf /etc/quagga/bgpd.conf.old
cp /usr/share/doc/quagga-*/bgpd.conf.sample /etc/quagga/bgpd.conf
systemctl start bgpd
systemctl enable bgpd
