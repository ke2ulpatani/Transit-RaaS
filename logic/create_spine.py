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

    spine_config_file = sys.argv[1]

    spine_name = spine_config_file.split('/')[-1].split('.')[0]

    if raas_utils.exists_spine(spine_name):
        print("Spine already exists")
        exit(1)

    #Assumed customer always gives correct config file
    spine_data = do_json.json_read(spine_config_file)

    hypervisor = spine_data["hypervisor_name"]

    hypervisors_data = do_json.json_read(constants.hypervisors_file)

    if hypervisor not in hypervisors_data:
        print("unknown hypervisor")
        exit(1)

    hypervisor_ip = hypervisors_data[hypervisor]["ip"]

    vpc_name = spine_data["vpc_name"]

    if not raas_utils.exists_vpc(vpc_name):
        print("VPC does not exist")
        exit(1)

    
    #All prereq checks done at this point
    spine_capacity = spine_data["capacity"]
    spine_name = spine_data["spine_name"]

    if spine_capacity == "f1"
        vcpu = 1
        mem = constants.1g_mem
    elif spine_capacity == "f2":
        vcpu = 2
        mem = constants.2g_mem
    elif spine_capacity == "f3":
        vcpu = 4
        mem = constants.4g_mem
    else:
        print("Unknown flavor using default")
        vcpu = 1
        mem = constants.1g_mem
    
    try:
        cid = raas_utils.get_client_id()
        sid = raas_utils.get_new_spine()
        image_arg = "image_path="+constants.img_path + \
                constants.spine_vm_img
        spine_name_ansible = "c" + cid + "_" + "s_" + spine_name
        spine_name_ansible_arg = spine_name
        c_s_image_path_arg = "c_s_image_path="+img_path+ \
                spine_name_ansible

        s_ram_arg = "s_ram=" + mem
        s_vcpu_arg = "s_vpu=" + vcpu

        mgt_net_arg = "mgt_net=c" + cid + "_m_net"


        extra_vars = constants.ansible_become_pass + " " + \
                image_arg + " " + c_mgt_path_arg + " " + \
                s_ram_arg + " " + s_vcpu_arg + " " + \
                mgt_net_arg

        try:
            os.system("ansible-playbook logic/misc/create_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raas_utils.add_mgmt_ns(hypervisor)
        except:
            os.system("ansible-playbook logic/misc/delete_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")

    raas_utils.add_vpc(vpc_name) 

    except:
        print("Cannot create management namspace")
