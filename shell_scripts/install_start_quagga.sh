#!/bin/bash

yum install -y quagga
setsebool zebra_write_config 1
cp /etc/quagga/zebra.conf /etc/quagga/zebra.conf.old
cp /usr/share/doc/quagga-*/zebra.conf.sample /etc/quagga/zebra.conf
systemctl start zebra
systemctl enable zebra
