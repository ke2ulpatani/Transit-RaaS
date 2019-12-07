import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress

"""@params:
    param1 = vpc config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give vpc config file")
        exit(1)

    leaf_config_file = sys.argv[1]

    leaf_name = leaf_config_file.split('/')[-1].split('.')[0]

    #Assumed customer always gives correct config file
    leaf_data = do_json.json_read(leaf_config_file)

    hypervisor = leaf_data["hypervisor_name"]
    hypervisor_arg = "hypervisor="+hypervisor

    hypervisors_data = hyp_utils.get_hypervisors_data()

    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

    vpc_name = leaf_data["vpc_name"]

    if not raas_utils.client_exists_vpc(vpc_name):
        print("VPC does not exist")
        exit(1)

    if raas_utils.client_exists_leaf(vpc_name, leaf_name):
        print("leaf already exists")
        exit(1)
    
    #All prereq checks done at this point
    leaf_name = leaf_data["leaf_name"]
    network_id = leaf_data["network_id"]

    cid = hyp_utils.get_client_id()

    try:
        #create leaf
        try:
            #l_name: leaf_name, l_net: network_name_br: L_br: name_br; 
            #hypervisor: hyp_name, l_ip, ve_l_br, ve_br_l, dhcp_range
            print("here")
            lid = hyp_utils.get_leaf_id(hypervisor, vpc_name)
            print(lid)
            leaf_name_hyp = "c" + str(cid) + "_" + "l" + str(lid)
            leaf_name_hyp_arg = "l_name="+leaf_name_hyp

            subnet = network_id.split('/')
            l_ip_arg = "l_ip=" + str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
            dhcp_range_arg = "dhcp_range=" + str(ipaddress.ip_address(subnet[0])+2)+','+ \
                    str(ipaddress.ip_address(subnet[0])+254)
            l_br_arg = "l_br=" + leaf_name_hyp + "_br"
            l_net_arg = "l_net=" + leaf_name_hyp + "_net"
            ve_l_br_arg = "ve_l_br=c" + str(cid) + "_ve_" + "l" + str(lid) + "_br"
            ve_br_l_arg = "ve_br_l=c" + str(cid) + "_ve_" + "br_l" + str(lid)

            extra_vars = constants.ansible_become_pass + " " + \
                    leaf_name_hyp_arg + " " + l_ip_arg + " " + \
                    dhcp_range_arg + " " + l_br_arg + " " + \
                    l_net_arg + " " + ve_l_br_arg + " " + \
                    ve_br_l_arg + " " + hypervisor_arg


            print("ansible-playbook logic/subnet/create_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            rc = os.system("ansible-playbook logic/subnet/create_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                raise

            hyp_utils.write_leaf_id(lid+1, vpc_name, hypervisor)
            hyp_utils.vpc_add_leaf(hypervisor, vpc_name, leaf_name, leaf_name_hyp)
            raas_utils.client_add_leaf(vpc_name, leaf_name)

        except:
            os.system("ansible-playbook logic/subnet/delete_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            print("ansible-playbook logic/subnet/delete_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raise


        #connect to available spines
        spines_data = hyp_utils.get_spines_data(hypervisor, vpc_name)

        for each in spines_data:
            print(each)
    except:
        print("create leaf failed")
