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
        print("VPC does not exist")
        exit(1)

    if raas_utils.client_exists_spine(vpc_name, spine_name):
        print("Spine already exists")
        exit(1)
    
    #All prereq checks done at this point
    spine_capacity = spine_data["capacity"]
    spine_name = spine_data["spine_name"]

    if spine_capacity == "f1":
        vcpu = "1,1"
        mem = constants.f1_mem
    elif spine_capacity == "f2":
        vcpu = "1,2"
        mem = constants.f2_mem
    elif spine_capacity == "f3":
        vcpu = "1,3"
        mem = constants.f3_mem
    else:
        print("Unknown flavor using default")
        vcpu = 1
        mem = constants.f1_mem
    
    cid = hyp_utils.get_client_id()
    vpcid = hyp_utils.get_hyp_vpc_name(hypervisor, vpc_name)

    try:
        #create_spine
        try:
            sid = hyp_utils.get_spine_id(hypervisor, vpc_name)
            image_arg = "image_path="+constants.img_path + \
                    constants.spine_vm_img
            spine_name_ansible = vpcid + "_" + "s" + str(sid)
            spine_name_ansible_arg = "s_name="+spine_name_ansible
            c_s_image_path_arg = "c_s_image_path="+constants.img_path+ \
                    spine_name_ansible + ".img"

            s_ram_arg = "s_ram=" + str(mem)
            s_vcpu_arg = "s_vcpu=" + str(vcpu)

            mgt_net_arg = "mgt_net=" + hyp_utils.get_mgmt_net(cid)

            extra_vars = constants.ansible_become_pass + " " + \
                    image_arg + " " +  \
                    s_ram_arg + " " + s_vcpu_arg + " " + \
                    mgt_net_arg + " " + spine_name_ansible_arg + \
                    " " + c_s_image_path_arg + " " +  hypervisor_arg

            #print("here2")
            print("ansible-playbook logic/vpc/create_spine.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raise
            rc = os.system("ansible-playbook logic/vpc/create_spine.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                raise
                
            hyp_utils.write_spine_id(sid+1, vpc_name, hypervisor)
            #print("here4", spine_name, vpc_name, hypervisor, spine_name_ansible)
            hyp_utils.vpc_add_spine(hypervisor, vpc_name, spine_name, spine_name_ansible)
            raas_utils.client_add_spine(hypervisor, vpc_name, spine_name, spine_capacity)

            #raise
            #raas_utils.add_mgmt_ns(hypervisor)
        except:
            print("create spine failed")
            print("ansible-playbook logic/vpc/delete_spine.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            os.system("ansible-playbook logic/vpc/delete_spine.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raise
        #print("ansible-playbook logic/vpc/delete_spine.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")

        #print("here3", sid+1, vpc_name, hypervisor)


        #get spine management ip
        try:
            vm_name_arg = "vm_name="+spine_name_ansible
            ip_file_path_arg = "ip_path=../../"+constants.temp_file
            net_name_arg = "net_name=c" + str(cid) + "_m_net"
            extra_vars = constants.ansible_become_pass + " " + \
                    " " + vm_name_arg + " " +  hypervisor_arg + " " + ip_file_path_arg + " " + net_name_arg
 
            print("ansible-playbook logic/misc/get_vm_ip.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            rc = os.system("ansible-playbook logic/misc/get_vm_ip.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                print ("get_vm_ip playbook failed")
                raise

            spine_ip = raas_utils.read_temp_file()
            print(spine_ip, vpc_name, spine_name)
            #raas_utils.write_spine_ip(vpc_name, spine_name, spine_ip)
        except:
            print("spine ip get and store failed")
            raise

        #instal quagga
        try:
            #spine_ip = raas_utils.get_spine_ip(vpc_name, spine_name)
            print("here1")
            spine_ip_arg = "vm_ip="+spine_ip
            print("here2", spine_ip_arg)

            ######
            extra_vars = constants.ansible_become_pass + " " + \
                    " " + spine_ip_arg

            print(extra_vars, "here2.3")
            ssh_common_args = "-o ProxyCommand=\"ssh -i " + constants.ssh_file + " ece792@" + hypervisor_ip + " " +\
                    "-W %h:%p\""
            print("here3", ssh_common_args)

            print("ansible-playbook logic/misc/quagga_install.yml -i \""+spine_ip+",\" -v --extra-vars '"+extra_vars+"'"\
                    + " --ssh-common-args='"+ssh_common_args+"'")
            rc = os.system("ansible-playbook logic/misc/quagga_install.yml -i \""+spine_ip+",\" -v --extra-vars '"+extra_vars+"'"\
                    + " --ssh-common-args='"+ssh_common_args+"'")
            if (rc != 0):
                raise
        except:
            print("quagga_install playbook failed")
            
            
        ##connect to available leafs
        #try:
        #  leaf_data = raas_utils.get_all_leafs(vpc_name)
        #  #l_s_net,l_s_br,ve_l_s,ve_s_l,s_name,l_name,subnet_ip,subnet_range
        #  #e.g. c1_br_l1_s1,c1_net_l1_s1,c1_ve_l1_s1,c1_ve_s1_l1,
        #  for leaf in leaf_data:
        #      leaf_id=hyp_utils.get_hyp_leaf_name(hypervisor,vpc_name,leaf).split('_')[2]
        #  
        #      network=raas_utils.get_new_veth_subnet('lns_spine')
        #      subnet = network.split('/')
        #      b_ip = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
        #      dhcp_range = str(ipaddress.ip_address(subnet[0])+2)+','+ \
        #              str(ipaddress.ip_address(subnet[0])+6)
        #      
        #       
        #      l_s_net=" l_s_net=" + vpcid + "_net_" + leaf_id+"_" + "s" + str(sid)
        #      l_s_br=" l_s_br=" + vpcid + "_br_" + leaf_id+"_" + "s" + str(sid)
        #      ve_l_s=" ve_l_s=" + vpcid + "_ve_" + leaf_id+"_" + "s" + str(sid)
        #      ve_s_l=" ve_s_l=" + vpcid + "_ve_" + "s" + str(sid) +"_" + leaf_id
        #      s_name_arg=" s_name="+spine_id
        #      l_name_arg=" l_name="+leaf_name_hyp
        #      subnet_ip_arg=" subnet_ip="+b_ip
        #      subnet_range_arg=" subnet_range="+dhcp_range
        #      
        #      extra_vars = constants.ansible_become_pass + l_s_net_arg + l_s_br_arg + ve_l_s_arg + ve_s_l_arg + s_name_arg + l_name_arg + subnet_ip_arg + subnet_range_arg + " " + hypervisor_arg
        #      
        #      raas_utils.run_shell_script("ansible-playbook logic/subnet/connect_leaf_spine.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
        #      
        #      new_subnet=str(ipaddress.ip_address(subnet[0])+8) + '/' + subnet[1]
        #      raas_utils.update_veth_subnet('lns_spine',new_subnet)
        #      
        #except Exception as e:
        #    print("Connecting leaf to spines failed: ",e)
        #    raise
    except:
        print("create spine failed python failed")
