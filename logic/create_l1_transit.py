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
        vcpu = "1,1"
        mem = "1G"
    elif l1_transit_capacity == "f2":
        vcpu = "1,2"
        mem = "2G"
    elif l1_transit_capacity == "f3":
        vcpu = "1,3"
        mem = "4G"
    else:
        print("Unknown flavor using default")
        vcpu = "1,1"
        mem = "1G"
    
    cid = hyp_utils.get_client_id()

    try:
        #create transit
        try:
            l1id = hyp_utils.get_l1_transit_id(hypervisor)
            l1_transit_name_ansible = "c"+ str(cid) + "_" + "l1t" + str(l1id)
            l1_transit_name_ansible_arg = "c_name="+l1_transit_name_ansible

            t_ram_arg = "c_ram=" + str(mem)
            t_vcpu_arg = "c_vcpu=" + str(vcpu)

            extra_vars = constants.ansible_become_pass + " " + \
                    t_ram_arg + " " + t_vcpu_arg + " " + \
                    l1_transit_name_ansible_arg + " " + \
                    hypervisor_arg

            print("ansible-playbook logic/misc/create_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            rc = raas_utils.run_playbook("ansible-playbook logic/misc/create_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                raise

            hyp_utils.write_l1_transit_id(l1id+1, hypervisor)
            hyp_utils.hyp_add_l1_transit(hypervisor, l1_transit_name, l1_transit_name_ansible)
            raas_utils.client_add_l1_transit(hypervisor, l1_transit_name, l1_transit_capacity)

        except Exception as e:
            print("create l1_transit failed deleting transit", e)
            raas_utils.run_playbook("ansible-playbook logic/misc/delete_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raise

        #configure transit
        try:
            t_name_arg = "t_name="+l1_transit_name_ansible

            t_loopback_ip = raas_utils.get_new_veth_subnet('loopbacks')
            t_loopback_ip_arg = "t_loopback_ip="+str(t_loopback_ip)

            network=raas_utils.get_new_veth_subnet('l1t_h')
            subnet = network.split('/')

            t_h_ip = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
            t_h_ip_arg = "t_h_ip="+t_h_ip

            h_t_ip = str(ipaddress.ip_address(subnet[0])+2) + '/' + subnet[1]
            h_t_ip_arg = "h_t_ip="+h_t_ip

            c_hyp_id = l1_transit_name_ansible.split('_')[0]
            t_hyp_id = l1_transit_name_ansible.split('_')[1]

            ve_t_h_arg = "ve_t_h=" + c_hyp_id + '_ve_' + t_hyp_id + '_h'
            ve_h_t_arg = "ve_h_t=" + c_hyp_id + '_ve_h_' + t_hyp_id 

            extra_vars = constants.ansible_become_pass + " "\
                     + t_name_arg + " " + t_loopback_ip_arg + \
                    " "  +  hypervisor_arg + \
                    " " + t_h_ip_arg + " " + h_t_ip_arg + " " + \
                    " " + ve_t_h_arg + " " + ve_h_t_arg

            rc = raas_utils.run_playbook("ansible-playbook logic/transit/configure_transit.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                raise

            new_subnet=str(ipaddress.ip_address(subnet[0])+4) + '/' + subnet[1]
            raas_utils.update_veth_subnet('l1t_h',new_subnet)

            subnet = t_loopback_ip.split('/')
            new_subnet = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
            raas_utils.update_veth_subnet('loopbacks',new_subnet)

        except Exception as e:
            print("create transit failed ", e)
            raise
    except Exception as e:
        print("create l1_transit failed python failed ", e)
