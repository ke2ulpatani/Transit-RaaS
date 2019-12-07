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
        vcpu = 1
        mem = constants.f1_mem
    elif pc_capacity == "f2":
        vcpu = 2
        mem = constants.f2_mem
    elif pc_capacity == "f3":
        vcpu = 4
        mem = constants.f3_mem
    else:
        print("Unknown flavor using default")
        vcpu = 1
        mem = constants.f1_mem
    
    cid = hyp_utils.get_client_id()

    try:
        #create_pc
        try:
            pcid = hyp_utils.get_pc_id(hypervisor, vpc_name)
            image_arg = "image_path="+constants.img_path + \
                    constants.pc_vm_img
            pc_name_ansible = "c" + str(cid) + "_" + "vm" + str(pcid)
            pc_name_ansible_arg = "vm_name="+pc_name_ansible
            c_s_image_path_arg = "c_vm_image_path="+constants.img_path+ \
                    pc_name_ansible + ".img"

            s_ram_arg = "vm_ram=" + str(mem)
            s_vcpu_arg = "vm_vcpu=" + str(vcpu)

            mgt_net_arg = "mgt_net=" + hyp_utils.get_mgmt_net(cid)

            extra_vars = constants.ansible_become_pass + " " + \
                    image_arg + " " +  \
                    s_ram_arg + " " + s_vcpu_arg + " " + \
                    mgt_net_arg + " " + pc_name_ansible_arg + \
                    " " + c_s_image_path_arg + " " +  hypervisor_arg

            #print("here2")
            print("ansible-playbook logic/vpc/create_pc.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            rc = os.system("ansible-playbook logic/vpc/create_pc.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                raise
                
            hyp_utils.write_pc_id(pcid+1, vpc_name, hypervisor)
            #print("here4", pc_name, vpc_name, hypervisor, pc_name_ansible)
            hyp_utils.vpc_add_pc(hypervisor, vpc_name, pc_name, pc_name_ansible)
            raas_utils.client_add_pc(vpc_name, pc_name)

            #raise
            #raas_utils.add_mgmt_ns(hypervisor)
        except:
            print("create pc failed")
            print("ansible-playbook logic/vpc/delete_pc.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            os.system("ansible-playbook logic/vpc/delete_pc.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raise
        #print("ansible-playbook logic/vpc/delete_pc.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")

    except:
        print("create pc failed python failed")
