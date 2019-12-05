import os
import sys
#from do_json import *
import do_json
import raas_utils
import constants
import ipaddress

"""@params:
    param1 = vpc config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give vpc config file")
        exit(1)

    vpc_config_file = sys.argv[1]

    #Assumed customer always gives correct config file
    vpc_data = do_json.json_read(vpc_config_file)

    hypervisor = vpc_data["hypervisor_name"]

    hypervisors_data = do_json.json_read(constants.hypervisors_file)

    if hypervisor not in hypervisors_data:
        print("unknown hypervisor")
        exit(1)

    hypervisor_ip = hypervisors_data[hypervisor]["ip"]

    if not raas_utils.exists_mgmt_ns(hypervisor):
        cid = raas_utils.get_client_id()
        mgmt_nid = raas_utils.get_mgmt_nid()

        nsm = "nsm=c" + cid + "_" + "nsm"
        b_net = "b_net=c" + cid + "_m_net"
        b = "b=c" + cid + "_m_b"
        nid = "nid=" + mgmt_nid
        ve_h_nsm = "ve_h_nsm=c" + cid + "ve_h_nsm"
        ve_nsm_h = "ve_nsm_h=c" + cid + "ve_nsm_h"
        ve_nsm_b = "ve_nsm_b=c" + cid + "ve_nsm_b"
        ve_b_nsm = "ve_b_nsm=c" + cid + "ve_b_nsm"
        h_nsm_ip = "h_nsm_ip=" + raas_utils.get_h_nsm_ip(hypervisor)
        nsm_h_ip = "nsm_h_ip=" + raas_utils.get_nsm_h_ip(hypervisor)

        subnet = mgmt_nid.split('/')
        b_ip = "b_ip=" + str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
        dhcp_range = "dhcp_range=" + str(ipaddress.ip_address(subnet[0])+2)+','+ \
                str(ipaddress.ip_address(subnet[0])+254)

        extra_vars = constants.ansible_become_pass + " " + nsm + " " + b_net + " " + b + " " + \
                nid + " " + ve_h_nsm + " " + ve_nsm_h + " " + \
                ve_nsm_b + " " + ve_b_nsm + " " + h_nsm_ip + \
                " " + nsm_h_ip + " " + b_ip + " " + dhcp_range

        ec = os.system("ansible-playbook logic/misc/create_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
        if ec == 0:
            raas_utils.add_mgmt_ns(hypervisor)
