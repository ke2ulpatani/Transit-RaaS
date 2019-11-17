#!/bin/bash
import sys
import libvirt
if __name__ == "__main__":
    vm_name = str(sys.argv[1])
    source_name = "eth1"
    conn = libvirt.open('qemu:///system')
    dom = conn.lookupByName(vm_name)
    ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
    iface = ifaces[source_name]
    for addr in iface["addrs"]:
        if addr["type"] == 0:
            print addr["addr"]