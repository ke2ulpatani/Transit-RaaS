import os
import sys
import do_json
import raas_utils
import constants
import ipaddress
import hyp_utils
from subprocess import Popen, PIPE

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
    hypervisor_arg = "hypervisor=" + hypervisor

    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

    #print("here1")

    cid = None
    cid = hyp_utils.get_client_id()
    try:
        if not hyp_utils.exists_mgmt_ns(hypervisor):
            mgmt_nid = raas_utils.get_mgmt_nid()

            nsm = "nsm=c" + cid + "_" + "nsm"
            b_net = "b_net=c" + cid + "_m_net"
            b = "c" + cid + "_m_b"
            b_arg = "b=c" + cid + "_m_b"
            nid = "nid=" + mgmt_nid
            ve_h_nsm = "ve_h_nsm=c" + cid + "ve_h_nsm"
            ve_nsm_h = "ve_nsm_h=c" + cid + "ve_nsm_h"
            ve_nsm_b = "ve_nsm_b=c" + cid + "ve_nsm_b"
            ve_b_nsm = "ve_b_nsm=c" + cid + "ve_b_nsm"
            h_nsm_ip = "h_nsm_ip=" + hyp_utils.get_h_nsm_ip(hypervisor)
            nsm_h_ip = hyp_utils.get_nsm_h_ip(hypervisor)
            nsm_h_ip_arg = "nsm_h_ip=" + nsm_h_ip

            subnet = mgmt_nid.split('/')
            b_ip = "b_ip=" + str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
            dhcp_range = "dhcp_range=" + str(ipaddress.ip_address(subnet[0])+2)+','+ \
                    str(ipaddress.ip_address(subnet[0])+254)

            nsm_h_route = nsm_h_ip.split('/')[0]
            nsm_h_route_arg = "nsm_h_route=" + nsm_h_route

            extra_vars = constants.ansible_become_pass + " " + nsm + " " + b_net + " " + b_arg + " " + \
                    nid + " " + ve_h_nsm + " " + ve_nsm_h + " " + \
                    ve_nsm_b + " " + ve_b_nsm + " " + h_nsm_ip + \
                    " " + nsm_h_ip + " " + b_ip + " " + dhcp_range + " " + hypervisor_arg + " " + nsm_h_route_arg
            #print("here2")

            try:
                #print("ansible-playbook logic/misc/create_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
                subprocess.call(["ansible-playbook", "logic/misc/create_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'"])
                #os.system("ansible-playbook logic/misc/create_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
                #p = Popen(subproc, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                #output, err = p.communicate(b"input data that is passed to subprocess' stdin")
                hyp_utils.add_mgmt_ns(hypervisor)
                hyp_utils.add_nsm_br(b, hypervisor)
            except Exception:
                print("create mgmt ns failed")
                #print("ansible-playbook logic/misc/delete_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
                subprocess.call("ansible-playbook logic/misc/delete_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
                raise

        vpc_id = hyp_utils.get_vpc_id(hypervisor)
        hyp_utils.write_vpc_id(vpc_id+1, hypervisor)
        #print(vpc_id, cid)

        hyp_vpc_name = "c" + cid + "_" + "v" + str(vpc_id)

        #print("here3")
        hyp_utils.hyp_add_vpc(hypervisor, vpc_name, hyp_vpc_name)

        raas_utils.client_add_vpc(vpc_name) 
        #print("here4")
    except Exception:
        print ("create vpc failed")
