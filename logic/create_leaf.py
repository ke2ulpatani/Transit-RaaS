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
    vpc_id=hyp_utils.get_hyp_vpc_name(hypervisor,vpc_name)

    if not raas_utils.client_exists_vpc(vpc_name):
        print("VPC does not exist")
        exit(1)

    if raas_utils.client_exists_leaf(vpc_name, leaf_name):
        print("leaf already exists")
        exit(1)
    
    #All prereq checks done at this point
    leaf_name = leaf_data["leaf_name"]
    network_id = leaf_data["network_id"]

    cid = hyp_utils.get_client_id()

    try:
        #create leaf
        try:
            #l_name: leaf_name, l_net: network_name_br: L_br: name_br; 
            #hypervisor: hyp_name, l_ip, ve_l_br, ve_br_l, dhcp_range
            print("here")
            lid = hyp_utils.get_leaf_id(hypervisor, vpc_name)
            print(lid)
            leaf_name_hyp = vpc_id + "_" + "l" + str(lid)
            leaf_name_hyp_arg = "l_name="+leaf_name_hyp

            subnet = network_id.split('/')
            l_ip_arg = "l_ip=" + str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
            dhcp_range_arg = "dhcp_range=" + str(ipaddress.ip_address(subnet[0])+2)+','+ \
                    str(ipaddress.ip_address(subnet[0])+254)
            l_br_arg = "l_br=" + leaf_name_hyp + "_br"
            l_net_arg = "l_net=" + leaf_name_hyp + "_net"
            ve_l_br_arg = "ve_l_br=" + vpc_id + "_ve_" + "l" + str(lid) + "_br"
            ve_br_l_arg = "ve_br_l=" + vpc_id + "_ve_" + "br_l" + str(lid)

            extra_vars = constants.ansible_become_pass + " " + \
                    leaf_name_hyp_arg + " " + l_ip_arg + " " + \
                    dhcp_range_arg + " " + l_br_arg + " " + \
                    l_net_arg + " " + ve_l_br_arg + " " + \
                    ve_br_l_arg + " " + hypervisor_arg


            print("ansible-playbook logic/subnet/create_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            rc = os.system("ansible-playbook logic/subnet/create_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                raise

            hyp_utils.write_leaf_id(lid+1, vpc_name, hypervisor)
            hyp_utils.vpc_add_leaf(hypervisor, vpc_name, leaf_name, leaf_name_hyp)
            raas_utils.client_add_leaf(hypervisor, vpc_name, leaf_name, network_id)

        except Exception as e:
            print("Creating leaf failed: ",e)
            raise
        
        
        #connect to available spines
        try:
          spines_data = raas_utils.get_all_spines(vpc_name)
          #l_s_net,l_s_br,ve_l_s,ve_s_l,s_name,l_name,subnet_ip,subnet_range
          #e.g. c1_br_l1_s1,c1_net_l1_s1,c1_ve_l1_s1,c1_ve_s1_l1,
          spine_ips=[]
          
          ssh_common_args = " --ssh-common-args='-o ProxyCommand=\"ssh -i " + constants.ssh_file + " ece792@" + hypervisor_ip + " '" +\
                    "-W %h:%p\""
          
          for spine in spines_data:
              spine_id=hyp_utils.get_hyp_spine_name(hypervisor,vpc_name,spine)
          
              network=raas_utils.get_new_veth_subnet('lns_spine')
              subnet = network.split('/')
              b_ip = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
              dhcp_range = str(ipaddress.ip_address(subnet[0])+2)+','+ \
                      str(ipaddress.ip_address(subnet[0])+6)
              
              net_name=vpc_id + "_net_l" + str(lid)+"_" + spine_id.split('_')[2]
              
              l_s_net_arg=" l_s_net=" +net_name 
              l_s_br_arg=" l_s_br=" + vpc_id + "_br_l" + str(lid)+"_" + spine_id.split('_')[2]
              ve_l_s_arg=" ve_l_s=" + vpc_id + "_ve_l" + str(lid)+"_" + spine_id.split('_')[2]
              ve_s_l_arg=" ve_s_l=" + vpc_id + "_ve_" + spine_id.split('_')[2] +"_l" + str(lid)
              s_name_arg=" s_name="+spine_id
              l_name_arg=" l_name="+leaf_name_hyp
              subnet_ip_arg=" subnet_ip="+b_ip
              subnet_range_arg=" subnet_range="+dhcp_range
              
              extra_vars = constants.ansible_become_pass + l_s_net_arg + l_s_br_arg + ve_l_s_arg + ve_s_l_arg + s_name_arg + l_name_arg + subnet_ip_arg + subnet_range_arg + " " + hypervisor_arg
              
              raas_utils.run_shell_script("ansible-playbook logic/subnet/connect_leaf_spine.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
              new_subnet=str(ipaddress.ip_address(subnet[0])+8) + '/' + subnet[1]
              raas_utils.update_veth_subnet('lns_spine',new_subnet)
              
              #Add route for leaf on spine
              
              
              spine_ip=raas_utils.get_vm_ip(hypervisor,spine_id,net_name)
              spine_ips.append(spine_ip)
              leaf_ip=raas_utils.get_vm_ip(hypervisor,leaf_name_hyp,net_name)
              
              mgmt_spine_ip=get_vm_ip(hypervisor,spine_id,"c"+str(cid)+"_m_net")
              mgmt_spine_ip_arg = " vm_ip="+mgmt_spine_ip
              route_cmd_arg=" route_cmd=add "+network_id+ " via "+leaf_ip
              extra_vars=mgmt_spine_ip_arg+route_cmd_arg
              raas_utils.run_shell_script("ansible-playbook logic/misc/add_route.yml -i "+mgmt_spine_ip+" -v --extra-vars '"+extra_vars+"'"+ssh_common_args)
             
          route_weight="ip route add default scope global" 
          for curr_ip in spine_ips:
               route_weight+=" nexthop via "+curr_ip+" weight 1"

          mgmt_leaf_ip=get_vm_ip(hypervisor,leaf_name_hyp,"c"+str(cid)+"_m_net")
          mgmt_leaf_ip_arg = " vm_ip="+mgmt_leaf_ip
          route_cmd_arg=" route_cmd="+route_weight
          extra_vars=mgmt_leaf_ip_arg+route_cmd_arg
          raas_utils.run_shell_script("ansible-playbook logic/misc/add_route.yml -i "+mgmt_leaf_ip+" -v --extra-vars '"+extra_vars+"'"+ssh_common_args)
    
        except Exception as e:
            print("Connecting leaf to spines failed: ",e)
            raise
    except Exception as e:
        raas_utils.run_shell_script("ansible-playbook logic/subnet/delete_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")