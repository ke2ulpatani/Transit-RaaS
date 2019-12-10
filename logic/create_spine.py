import os
import sys
#from do_json import *
import do_json
import hyp_utils
import constants
import ipaddress
import raas_utils

"""@params:
    param1 = vpc config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        raas_utils.log_service("Please give vpc config file")
        exit(1)

    spine_config_file = sys.argv[1]

    spine_name = spine_config_file.split('/')[-1].split('.')[0]

    #Assumed customer always gives correct config file
    spine_data = do_json.json_read(spine_config_file)

    hypervisor = spine_data["hypervisor_name"]
    hypervisor_arg = "hypervisor="+hypervisor

    hypervisors_data = hyp_utils.get_hypervisors_data()

    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

    vpc_name = spine_data["vpc_name"]

    if not raas_utils.client_exists_vpc(vpc_name):
        raas_utils.log_service("VPC does not exist")
        exit(1)

    if raas_utils.client_exists_spine(vpc_name, spine_name):
        raas_utils.log_service("Spine already exists")
        exit(1)
    
    #All prereq checks done at this point
    spine_capacity = spine_data["capacity"]
    spine_name = spine_data["spine_name"]
    self_as = spine_data["self_as"]

    if spine_capacity == "f1":
        vcpu = "1,1"
        mem = "1G"
    elif spine_capacity == "f2":
        vcpu = "1,2"
        mem = "2G"
    elif spine_capacity == "f3":
        vcpu = "1,3"
        mem = "4G"
    else:
        raas_utils.log_service("Unknown flavor using default")
        vcpu = 1
        mem = "1G"
    
    cid = hyp_utils.get_client_id()
    vpcid = hyp_utils.get_hyp_vpc_name(hypervisor, vpc_name)

    try:
        #create_spine
        try:
            sid = hyp_utils.get_spine_id(hypervisor, vpc_name)
            spine_name_ansible = vpcid + "_" + "s" + str(sid)
            spine_name_ansible_arg = "c_name="+spine_name_ansible

            s_ram_arg = "c_ram=" + str(mem)
            s_vcpu_arg = "c_vcpu=" + str(vcpu)

            extra_vars = constants.ansible_become_pass + " " + \
                    s_ram_arg + " " + s_vcpu_arg + " " + \
                    " " +  hypervisor_arg + " " + spine_name_ansible_arg

            rc = raas_utils.run_playbook("ansible-playbook logic/misc/create_router_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                raise
                
            hyp_utils.write_spine_id(sid+1, vpc_name, hypervisor)
            hyp_utils.vpc_add_spine(hypervisor, vpc_name, spine_name, spine_name_ansible)
            raas_utils.client_add_spine(hypervisor, vpc_name, spine_name, spine_capacity, self_as)

        except:
            raas_utils.log_service("create spine failed")
            os.system("ansible-playbook logic/misc/delete_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raise
    except:
        raas_utils.log_service("create spine failed python failed")
