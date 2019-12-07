import os
import sys
#from do_json import *
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

    transit_l1_config_file = sys.argv[1]

    transit_l1_name = transit_l1_config_file.split('/')[-1].split('.')[0]

    #Assumed customer always gives correct config file
    transit_l1_data = do_json.json_read(transit_l1_config_file)

    hypervisor = transit_l1_data["hypervisor_name"]
    hypervisor_arg = "hypervisor="+hypervisor

    hypervisors_data = hyp_utils.get_hypervisors_data()

    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

    vpc_name = transit_l1_data["vpc_name"]

    if not raas_utils.client_exists_vpc(vpc_name):
        print("VPC does not exist")
        exit(1)

    if raas_utils.client_exists_transit_l1(vpc_name, transit_l1_name):
        print("Spine already exists")
        exit(1)
    
    #All prereq checks done at this point
    transit_l1_capacity = transit_l1_data["capacity"]
    transit_l1_name = transit_l1_data["transit_l1_name"]

    if transit_l1_capacity == "f1":
        vcpu = 1
        mem = constants.f1_mem
    elif transit_l1_capacity == "f2":
        vcpu = 2
        mem = constants.f2_mem
    elif transit_l1_capacity == "f3":
        vcpu = 4
        mem = constants.f3_mem
    else:
        print("Unknown flavor using default")
        vcpu = 1
        mem = constants.f1_mem
    
    cid = hyp_utils.get_client_id()

    try:
        #create_transit_l1
        try:
            sid = hyp_utils.get_transit_l1_id(hypervisor, vpc_name)
            image_arg = "image_path="+constants.img_path + \
                    constants.transit_l1_vm_img
            transit_l1_name_ansible = "c" + str(cid) + "_" + "s" + str(sid)
            transit_l1_name_ansible_arg = "s_name="+transit_l1_name_ansible
            c_s_image_path_arg = "c_s_image_path="+constants.img_path+ \
                    transit_l1_name_ansible + ".img"

            s_ram_arg = "s_ram=" + str(mem)
            s_vcpu_arg = "s_vcpu=" + str(vcpu)

            mgt_net_arg = "mgt_net=" + hyp_utils.get_mgmt_net(cid)

            extra_vars = constants.ansible_become_pass + " " + \
                    image_arg + " " +  \
                    s_ram_arg + " " + s_vcpu_arg + " " + \
                    mgt_net_arg + " " + transit_l1_name_ansible_arg + \
                    " " + c_s_image_path_arg + " " +  hypervisor_arg

            #print("here2")
            print("ansible-playbook logic/vpc/create_transit_l1.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            rc = os.system("ansible-playbook logic/vpc/create_transit_l1.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                raise
                
            hyp_utils.write_transit_l1_id(sid+1, vpc_name, hypervisor)
            #print("here4", transit_l1_name, vpc_name, hypervisor, transit_l1_name_ansible)
            hyp_utils.vpc_add_transit_l1(hypervisor, vpc_name, transit_l1_name, transit_l1_name_ansible)
            raas_utils.client_add_transit_l1(vpc_name, transit_l1_name)

            #raise
            #raas_utils.add_mgmt_ns(hypervisor)
        except:
            print("create transit_l1 failed")
            print("ansible-playbook logic/vpc/delete_transit_l1.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            os.system("ansible-playbook logic/vpc/delete_transit_l1.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raise
        #print("ansible-playbook logic/vpc/delete_transit_l1.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")

        #print("here3", sid+1, vpc_name, hypervisor)


        #get transit_l1 ip and store to some file
        try:
            vm_name_arg = "vm_name="+transit_l1_name_ansible
            ip_file_path_arg = "ip_path=../../"+constants.temp_file
            extra_vars = constants.ansible_become_pass + " " + \
                    " " + vm_name_arg + " " +  hypervisor_arg + " " + ip_file_path_arg

            print("ansible-playbook logic/misc/get_vm_ip.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            rc = os.system("ansible-playbook logic/misc/get_vm_ip.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                print ("get_vm_ip playbook failed")
                raise

            transit_l1_ip = raas_utils.read_temp_file()
            print(transit_l1_ip, vpc_name, transit_l1_name)
            raas_utils.write_transit_l1_ip(vpc_name, transit_l1_name, transit_l1_ip)
        except:
            print("transit_l1 ip get and store failed")
            raise

        #instal quagga
        try:
            transit_l1_ip = raas_utils.get_transit_l1_ip(vpc_name, transit_l1_name)
            print("here1")
            transit_l1_ip_arg = "vm_ip="+transit_l1_ip
            print("here2", transit_l1_ip_arg)

            ######
            extra_vars = constants.ansible_become_pass + " " + \
                    " " + transit_l1_ip_arg

            print(extra_vars, "here2.3")
            ssh_common_args = "-o ProxyCommand=\"ssh -i " + constants.ssh_file + " ece792@" + hypervisor_ip + " " +\
                    "-W %h:%p\""
            print("here3", ssh_common_args)

            print("ansible-playbook logic/misc/quagga_install.yml -i \""+transit_l1_ip+",\" -v --extra-vars '"+extra_vars+"'"\
                    + " --ssh-common-args='"+ssh_common_args+"'")
            rc = os.system("ansible-playbook logic/misc/quagga_install.yml -i \""+transit_l1_ip+",\" -v --extra-vars '"+extra_vars+"'"\
                    + " --ssh-common-args='"+ssh_common_args+"'")
            if (rc != 0):
                raise
        except:
            print("quagga_install playbook failed")
    except:
        print("create transit_l1 failed python failed")
