import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress
from logging import info as print
logging.basicConfig(filename='raas.log', filemode='a', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
"""@params:
    param1 = vpc config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give vpc config file")
        exit(1)

    pc_config_file = sys.argv[1]

    pc_name = pc_config_file.split('/')[-1].split('.')[0]

    #Assumed customer always gives correct config file
    pc_data = do_json.json_read(pc_config_file)

    hypervisor = pc_data["hypervisor_name"]
    hypervisor_arg = "hypervisor="+hypervisor

    hypervisors_data = hyp_utils.get_hypervisors_data()

    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

    vpc_name = pc_data["vpc_name"]

    if not raas_utils.client_exists_vpc(vpc_name):
        print("VPC does not exist")
        exit(1)

    if raas_utils.client_exists_pc(vpc_name, pc_name):
        print("Spine already exists")
        exit(1)
    
    #All prereq checks done at this point
    pc_capacity = pc_data["capacity"]
    pc_name = pc_data["pc_name"]

    if pc_capacity == "f1":
        vcpu = "1,1"
        mem = "1G"
    elif pc_capacity == "f2":
        vcpu = "1,2"
        mem = "2G"
    elif pc_capacity == "f3":
        vcpu = "1,3"
        mem = "4G"
    else:
        print("Unknown flavor using default")
        vcpu = "1,1"
        mem = "1G"
    
    cid = hyp_utils.get_client_id()
    hyp_vpc_name = hyp_utils.get_hyp_vpc_name(hypervisor, vpc_name)

    try:
        #create_pc
        try:
            pcid = hyp_utils.get_pc_id(hypervisor, vpc_name)
            #image_arg = "image_path="+constants.img_path + \
            #        constants.pc_vm_img

            pc_name_ansible = hyp_vpc_name + "_" + "vm" + str(pcid)
            pc_name_ansible_arg = "c_name="+pc_name_ansible
            #c_s_image_path_arg = "c_vm_image_path="+constants.img_path+ \
            #        pc_name_ansible + ".img"

            s_ram_arg = "c_ram=" + str(mem)
            s_vcpu_arg = "c_vcpu=" + str(vcpu)

            #mgt_net_arg = "mgt_net=" + hyp_utils.get_mgmt_net(cid)

            extra_vars = constants.ansible_become_pass + " " + \
                    s_ram_arg + " " + s_vcpu_arg + " " + \
                    pc_name_ansible_arg + \
                    " " + hypervisor_arg

            raas_utils.run_playbook("ansible-playbook logic/misc/create_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
                
            hyp_utils.write_pc_id(pcid+1, vpc_name, hypervisor)
            hyp_utils.vpc_add_pc(hypervisor, vpc_name, pc_name, pc_name_ansible)
            raas_utils.client_add_pc(hypervisor, vpc_name, pc_name, pc_capacity)
        except:
            print("create pc failed")
            raas_utils.run_playbook("ansible-playbook logic/misc/delete_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raise
    except:
        print("create pc failed python failed")
