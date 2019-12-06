import os
import sys
import do_json
import raas_utils
import constants
import ipaddress
import hyp_utils

"""@params:
    param1 = vpc config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give vpc config file")
        exit(1)

    vpc_config_file = sys.argv[1]

    vpc_name = vpc_config_file.split('/')[-1].split('.')[0]

    if raas_utils.client_exists_vpc(vpc_name):
        print("Vpc already exists")
        exit(1)

    #Assumed customer always gives correct config file
    vpc_config_data = do_json.json_read(vpc_config_file)

    hypervisor = vpc_config_data["hypervisor_name"]

    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

    try:
        if not hyp_utils.exists_mgmt_ns(hypervisor):
            cid = hyp_utils.get_client_id()
            mgmt_nid = raas_utils.get_mgmt_nid()

            nsm = "nsm=c" + cid + "_" + "nsm"
            b_net = "b_net=c" + cid + "_m_net"
            b = "b=c" + cid + "_m_b"
            nid = "nid=" + mgmt_nid
            ve_h_nsm = "ve_h_nsm=c" + cid + "ve_h_nsm"
            ve_nsm_h = "ve_nsm_h=c" + cid + "ve_nsm_h"
            ve_nsm_b = "ve_nsm_b=c" + cid + "ve_nsm_b"
            ve_b_nsm = "ve_b_nsm=c" + cid + "ve_b_nsm"
            h_nsm_ip = "h_nsm_ip=" + hyp_utils.get_h_nsm_ip(hypervisor)
            nsm_h_ip = "nsm_h_ip=" + hyp_utils.get_nsm_h_ip(hypervisor)

            subnet = mgmt_nid.split('/')
            b_ip = "b_ip=" + str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
            dhcp_range = "dhcp_range=" + str(ipaddress.ip_address(subnet[0])+2)+','+ \
                    str(ipaddress.ip_address(subnet[0])+254)

            extra_vars = constants.ansible_become_pass + " " + nsm + " " + b_net + " " + b + " " + \
                    nid + " " + ve_h_nsm + " " + ve_nsm_h + " " + \
                    ve_nsm_b + " " + ve_b_nsm + " " + h_nsm_ip + \
                    " " + nsm_h_ip + " " + b_ip + " " + dhcp_range

            try:
                os.system("ansible-playbook logic/misc/create_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
                hyp_utils.add_mgmt_ns(hypervisor)
                hyp_utils.add_nsm_br(b, hypervisor)
            except:
                os.system("ansible-playbook logic/misc/delete_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")

    vpc_id = hyp_utils.get_vpc_id(hypervisor)

    hyp_vpc_name = "c" + cid + "_" + "v" + vpc_id

    hyp_utils.hyp_add_vpc(hypervisor, vpc_name, hyp_vpc_name)

    raas_utils.client_add_vpc(vpc_name) 

    except:
        print("Cannot create management namspace")
