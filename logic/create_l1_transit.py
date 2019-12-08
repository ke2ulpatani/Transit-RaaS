import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress

"""@params:
    param1 = l1_transit config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give l1_transit config file")
        exit(1)

    l1_transit_config_file = sys.argv[1]

    l1_transit_name = l1_transit_config_file.split('/')[-1].split('.')[0]

    #Assumed customer always gives correct config file
    l1_transit_data = do_json.json_read(l1_transit_config_file)

    hypervisor = l1_transit_data["hypervisor_name"]
    hypervisor_arg = "hypervisor="+hypervisor

    hypervisors_data = hyp_utils.get_hypervisors_data()

    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

    if raas_utils.client_exists_l1_transit(l1_transit_name):
        print("l1_transit already exists ", l1_transit_name)
        exit(1)
    
    #All prereq checks done at this point
    l1_transit_capacity = l1_transit_data["capacity"]
    l1_transit_name = l1_transit_data["l1_transit_name"]

    if l1_transit_capacity == "f1":
        vcpu = 1
        mem = constants.f1_mem
    elif l1_transit_capacity == "f2":
        vcpu = 2
        mem = constants.f2_mem
    elif l1_transit_capacity == "f3":
        vcpu = 4
        mem = constants.f3_mem
    else:
        print("Unknown flavor using default")
        vcpu = 1
        mem = constants.f1_mem
    
    cid = hyp_utils.get_client_id()

    try:
        try:
            #image_path, c_t_image_path, t_name, t_ram, t_vcpu, mgt_net, t_h_net, t_h_br, hypervisor, b_ip, dhcp_range

            l1id = hyp_utils.get_l1_transit_id(hypervisor)
            l1_transit_name_ansible = "c"+ str(cid) + "_" + "l1t" + str(l1id)
            l1_transit_name_ansible_arg = "t_name="+l1_transit_name_ansible

            t_ram_arg = "t_ram=" + str(mem)
            t_vcpu_arg = "t_vcpu=" + str(vcpu)

            network=raas_utils.get_new_veth_subnet('l1t_h')
            subnet = network.split('/')
            b_ip = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
            b_ip_arg = "b_ip="+b_ip
            dhcp_range = str(ipaddress.ip_address(subnet[0])+2)+','+ \
                      str(ipaddress.ip_address(subnet[0])+2)
            dhcp_range_arg = "dhcp_range=" + dhcp_range
              
            t_h_net = l1_transit_name_ansible + "_h_net"
            t_h_net_arg = "t_h_net=" + t_h_net

            t_h_br = l1_transit_name_ansible + "_h_br"
            t_h_br_arg = "t_h_br=" + t_h_br

            extra_vars = constants.ansible_become_pass + " " + \
                    t_ram_arg + " " + t_vcpu_arg + " " + \ 
                     + l1_transit_name_ansible_arg + \
                    " "  +  hypervisor_arg + \
                    " " + t_h_net_arg + " " + t_h_br_arg + " " + b_ip_arg + \
                    " " + dhcp_range_arg

            rc = raas_utils.run_playbook("ansible-playbook logic/transit/create_transit.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                raise
                
            new_subnet=str(ipaddress.ip_address(subnet[0])+4) + '/' + subnet[1]
            raas_utils.update_veth_subnet('l1t_h',new_subnet)

            hyp_utils.write_l1_transit_id(l1id+1, hypervisor)
            hyp_utils.hyp_add_l1_transit(hypervisor, l1_transit_name, l1_transit_name_ansible)
            raas_utils.client_add_l1_transit(hypervisor, l1_transit_name, l1_transit_capacity)

        except Exception as e:
            print("create l1_transit failed deleting transit", e)
            #raas_utils.run_playbook("ansible-playbook logic/vpc/delete_l1_transit.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raise

        #get l1_transit management ip
        net_name = "c" + str(cid) + "_m_net"
        l1_transit_ip = raas_utils.get_vm_ip(hypervisor, l1_transit_name_ansible, net_name)
        print(l1_transit_ip, l1_transit_name)
        
        #configure l1 trasit
        try:
            #vm_ip, t_loopback_ip
            l1_transit_ip_arg = "vm_ip="+l1_transit_ip

            t_loopback_ip = raas_utils.get_new_veth_subnet('loopbacks')
            t_loopback_ip_arg = "t_loopback_ip="+t_loopback_ip

            ######
            extra_vars = constants.ansible_become_pass + " " + \
                    " " + l1_transit_ip_arg + " " + t_loopback_ip_arg

            print(extra_vars, "here2.3")
            ssh_common_args = "-o ProxyCommand=\"ssh -i " + constants.ssh_file + " ece792@" + hypervisor_ip + " " +\
                    "-W %h:%p\""
            print("here3", ssh_common_args)

            rc = raas_utils.run_playbook("ansible-playbook logic/transit/configure_transit.yml -i \""+l1_transit_ip+",\" -v --extra-vars '"+extra_vars+"'"\
                    + " --ssh-common-args='"+ssh_common_args+"'")
            if (rc != 0):
                raise

            subnet = t_loopback_ip.split('/')
            new_subnet = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
            raas_utils.update_veth_subnet('loopbacks',new_subnet)

        except Exception as e:
            print("configure transit playbook failed ", e)
    except Exception as e:
        print("create l1_transit failed python failed ", e)
