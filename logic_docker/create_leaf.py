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

    cid = hyp_utils.get_client_id()

    try:
        #create leaf
        try:
            lid = hyp_utils.get_leaf_id(hypervisor, vpc_name)
            leaf_name_hyp = "c" + str(cid) + "_" + "l" + str(sid)
            leaf_name_hyp_arg = "l_name="+leaf_name_hyp

            extra_vars = constants.ansible_become_pass + " " + \
                    image_arg + " " +  \
                    s_ram_arg + " " + s_vcpu_arg + " " + \
                    mgt_net_arg + " " + leaf_name_ansible_arg + \
                    " " + c_s_image_path_arg + " " +  hypervisor_arg

            print("ansible-playbook logic/vpc/create_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            rc = 1
            #rc = os.system("ansible-playbook logic/vpc/create_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                raise

            hyp_utils.write_leaf_id(lid+1, vpc_name, hypervisor)
            hyp_utils.vpc_add_leaf(hypervisor, vpc_name, leaf_name, leaf_name_hyp)
            raas_utils.client_add_leaf(vpc_name, leaf_name)

        except:
            #os.system("ansible-playbook logic/vpc/delete_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            print("ansible-playbook logic/vpc/delete_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")


        #connect to available spines
        spines_data = hyp_utils.get_spines_data(hypervisor, vpc_name)

        for each in spines_data:
            print each




    except:
        print("create leaf failed")
