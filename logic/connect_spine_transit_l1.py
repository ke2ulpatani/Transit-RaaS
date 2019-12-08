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
    if (len(sys.argv) < 3):
        print("Please give vm and subnet")
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
        #connect to available spines
        try:
          spines_data = raas_utils.get_all_spines(vpc_name)
          spine_ips=[]
          
          for spine in spines_data:
              spine_id=hyp_utils.get_hyp_spine_name(hypervisor,vpc_name,spine)
          
              network=raas_utils.get_new_veth_subnet('lns_spine')
              subnet = network.split('/')
              l_ip = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
              s_ip = str(ipaddress.ip_address(subnet[0])+2) + '/' + subnet[1]
              l_ip_arg = " ns1_ip=" + l_ip
              s_ip_arg = " ns2_ip=" + s_ip              
              
              ve_l_s = vpc_id + "_ve_l" + str(lid)+"_" + spine_id.split('_')[2]
              ve_l_s_arg=" ve_ns1_ns2=" + ve_l_s
              ve_s_l = vpc_id + "_ve_" + spine_id.split('_')[2] +"_l" + str(lid)
              ve_s_l_arg=" ve_ns2_ns1=" + ve_s_l

              l_name_arg=" ns1="+leaf_name_hyp
              s_name_arg=" ns2="+spine_id

              
              extra_vars = constants.ansible_become_pass + l_ip_arg + s_ip_arg + \
                      ve_l_s_arg + ve_s_l_arg + s_name_arg + l_name_arg + \
                      " " + hypervisor_arg
              
              raas_utils.run_shell_script("ansible-playbook logic/misc/connect_ns_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
              
              #update reserved_ip
              new_subnet=str(ipaddress.ip_address(subnet[0])+8) + '/' + subnet[1]
              raas_utils.update_veth_subnet('lns_spine',new_subnet)
              
              spine_ip=raas_utils.get_ns_ip(hypervisor,spine_id, ve_s_l)
              spine_ips.append(spine_ip)

              #Add route for leaf on spine only if dhcp_flag is true
              if (dhcp_flag):
                  leaf_ip=raas_utils.get_ns_ip(hypervisor,leaf_name_hyp,ve_l_s)
                  ns_name_arg=" ns_name="+spine_id
                  route_cmd_arg=" route_cmd=\"add "+network_id+ " via "+leaf_ip+"\""
                  extra_vars=constants.ansible_become_pass+ns_name_arg+route_cmd_arg+ " " + hypervisor_arg
                  raas_utils.run_shell_script("ansible-playbook logic/misc/add_route_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
             

          ns_name_arg=" ns_name="+leaf_name_hyp
    
          #delete default arg
          route_cmd_arg=" route_cmd=\"delete default\""
          extra_vars=constants.ansible_become_pass+ns_name_arg+route_cmd_arg+ " " + hypervisor_arg
          raas_utils.run_shell_script("ansible-playbook logic/misc/add_route_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")

          #add weightet default arg
          route_weight="add default scope global" 
          for curr_ip in spine_ips:
               route_weight+=" nexthop via "+curr_ip+" weight 1"
          route_weight='"'+route_weight+'"'
          print(route_weight)

          route_cmd_arg=" route_cmd="+route_weight
          extra_vars=constants.ansible_become_pass+ns_name_arg+route_cmd_arg+ " " + hypervisor_arg
          raas_utils.run_shell_script("ansible-playbook logic/misc/add_route_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
    
        except Exception as e:
            print("Connecting leaf to spines failed: ",e)
            raise

        hyp_utils.write_leaf_id(lid+1, vpc_name, hypervisor)
        hyp_utils.vpc_add_leaf(hypervisor, vpc_name, leaf_name, leaf_name_hyp)
        raas_utils.client_add_leaf(hypervisor, vpc_name, leaf_name, network_id)

    except Exception as e:
        extra_vars=constants.ansible_become_pass + " " + leaf_name_hyp_arg +  " " + hypervisor_arg
        raas_utils.run_shell_script("ansible-playbook logic/misc/delete_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
