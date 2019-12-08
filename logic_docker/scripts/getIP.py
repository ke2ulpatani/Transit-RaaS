#!/bin/bash
import sys
import libvirt
import subprocess

if __name__ == "__main__":
    vm_name = str(sys.argv[1])
    net_name = str(sys.argv[2])
    conn = libvirt.open('qemu:///system')
    mac_address = subprocess.check_output("virsh domiflist "+vm_name+" | grep "+net_name+" | sed 's/\s\+/,/g' | cut -d ',' -f 5",shell=True).strip()
    dom = conn.lookupByName(vm_name)
    ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
    for (name, val) in ifaces.iteritems():
        found=False
        if str(val['hwaddr'])==str(mac_address):
            for ipaddr in val['addrs']:
                if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                    print(ipaddr['addr'])
                    found=True
                    break
        if(found):
            break