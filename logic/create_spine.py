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
    hypervisor_arg = "hypervisor="+hypervisor

    hypervisors_data = hyp_utils.get_hypervisors_data()

    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

    vpc_name = spine_data["vpc_name"]

    if not raas_utils.exists_vpc(vpc_name):
        print("VPC does not exist")
        exit(1)
    
    #All prereq checks done at this point
    spine_capacity = spine_data["capacity"]
    spine_name = spine_data["spine_name"]

    if spine_capacity == "f1"
        vcpu = 1
        mem = constants.f1_mem
    elif spine_capacity == "f2":
        vcpu = 2
        mem = constants.f2_mem
    elif spine_capacity == "f3":
        vcpu = 4
        mem = constants.f3_mem
    else:
        print("Unknown flavor using default")
        vcpu = 1
        mem = constants.f1_mem
    
    cid = hyp_utils.get_client_id()

    try:
        sid = hyp_utils.get_spine_id(hypervisor, vpc_name)
        image_arg = "image_path="+constants.img_path + \
                constants.spine_vm_img
        spine_name_ansible = "c" + cid + "_" + "s" + str(sid)
        spine_name_ansible_arg = "s_name="+spine_name_ansible
        c_s_image_path_arg = "c_s_image_path="+img_path+ \
                spine_name_ansible

        s_ram_arg = "s_ram=" + str(mem)
        s_vcpu_arg = "s_vcpu=" + str(vcpu)

        mgt_net_arg = "mgt_net=" + get_mgmt_net(cid)

        extra_vars = constants.ansible_become_pass + " " + \
                image_arg + " " +  \
                s_ram_arg + " " + s_vcpu_arg + " " + \
                mgt_net_arg + " " + spine_name_ansible_arg + \
                " " + c_s_image_path_arg + " " +  hypervisor_arg

        try:
            #os.system("ansible-playbook logic/misc/create_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            print("ansible-playbook logic/misc/create_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            #raas_utils.add_mgmt_ns(hypervisor)
        except:
            #os.system("ansible-playbook logic/misc/delete_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            print("ansible-playbook logic/misc/delete_mgmt_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")

    #raas_utils.add_vpc(vpc_name) 

    except:
        print("Cannot create management namspace")
