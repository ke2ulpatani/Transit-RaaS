import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress
#import logging
#from logging import info as raas_utils.log_service
#logging.basicConfig(filename='raas.log', filemode='a', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

"""@params:
    param1 = leaf config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 3):
        raas_utils.log_service("Please give leaf config file")
        exit(1)

    leaf_config_file = sys.argv[1]

    #dhcp leaf or dummy leaf
    dhcp_flag = sys.argv[2]
    if (dhcp_flag == "true" or dhcp_flag == "True"):
        dhcp_flag = True
    else:
        dhcp_flag = False

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
        raas_utils.log_service("VPC does not exist")
        exit(1)

    if raas_utils.client_exists_leaf(vpc_name, leaf_name):
        raas_utils.log_service("leaf already exists")
        exit(1)
    
    #All prereq checks done at this point
    leaf_name = leaf_data["leaf_name"]
    network_id = leaf_data["network_id"]

    cid = hyp_utils.get_client_id()
    print('here1')
    try:
        #create leaf = #create container + create_bridge with dhcp
        try:
            #l_name: leaf_name, l_net: network_name_br: L_br: name_br; 
            #hypervisor: hyp_name, l_ip, ve_l_br, ve_br_l, dhcp_range
            
            lid = hyp_utils.get_leaf_id(hypervisor, vpc_name)
            raas_utils.log_service(lid)
            leaf_name_hyp = vpc_id + "_" + "l" + str(lid)
            leaf_name_hyp_arg = "c_name="+leaf_name_hyp
            print('here2')
            subnet = network_id.split('/')
            if (dhcp_flag):
                print('here3')
                l_ip_arg = " br_ip=" + str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
                dhcp_range_arg = "dhcp_range=" + str(ipaddress.ip_address(subnet[0])+2)+','+ \
                        str(ipaddress.ip_address(subnet[0])+254)
            print('here4')
            l_br_arg = "br_name=" + leaf_name_hyp + "_br"
            #l_net_arg = "l_net=" + leaf_name_hyp + "_net"
            #ve_l_br_arg = "ve_l_br=" + vpc_id + "_ve_" + "l" + str(lid) + "_br"
            #ve_br_l_arg = "ve_br_l=" + vpc_id + "_ve_" + "br_l" + str(lid)
            c_vcpu_arg = " c_vcpu="+"1,1"
            c_ram_arg = " c_ram="+"1G"

            #create container
            try:
                extra_vars = constants.ansible_become_pass + " " + \
                        leaf_name_hyp_arg + " " + hypervisor_arg + " " + c_vcpu_arg + c_ram_arg
                
                raas_utils.run_playbook("ansible-playbook logic/misc/create_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            except Exception as e:
                raas_utils.log_service("create container failed "+ str(e))
                raise

            l_name_arg = "l_name=" + leaf_name_hyp

            t_loopback_ip = raas_utils.get_new_veth_subnet('loopbacks')
            t_loopback_ip_arg = "t_loopback_ip="+str(t_loopback_ip)

            extra_vars = constants.ansible_become_pass + " " + \
                    l_name_arg + " " + " " + l_br_arg + " " + \
                    hypervisor_arg + " " + t_loopback_ip_arg

            if (dhcp_flag):
                extra_vars += l_ip_arg + " " + dhcp_range_arg 

            #create bridge (with or without dhcp decided by extra_vars)
            try:
                raas_utils.run_playbook("ansible-playbook logic/subnet/create_bridge.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            except Exception as e:
                raas_utils.log_service("create bridge failed "+ str(e))
                raise

            subnet = t_loopback_ip.split('/')
            new_subnet = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
            raas_utils.update_veth_subnet('loopbacks',new_subnet)

        except Exception as e:
            raas_utils.log_service("Creating leaf failed: "+str(e))
            raise
        
        
        #connect to available spines
        try:
          spines_data = raas_utils.get_all_spines(vpc_name)
          spine_ips=[]
          
          for spine in spines_data:
              spine_id=hyp_utils.get_hyp_spine_name(hypervisor,vpc_name,spine)
              if spine_id is None:
                 continue
              network=raas_utils.get_new_veth_subnet('lns_spine')
              subnet = network.split('/')
              l_ip = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
              s_ip = str(ipaddress.ip_address(subnet[0])+2) + '/' + subnet[1]
              l_ip_arg = " ns1_ip=" + l_ip
              s_ip_arg = " ns2_ip=" + s_ip              
              
              ve_l_s = vpc_id + "vel" + str(lid)+ spine_id.split('_')[2]
              ve_l_s_arg=" ve_ns1_ns2=" + ve_l_s
              ve_s_l = vpc_id + "ve" + spine_id.split('_')[2] +"l" + str(lid)
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

              leaf_ip=raas_utils.get_ns_ip(hypervisor,leaf_name_hyp,ve_l_s)
              ns_name_arg=" ns_name="+spine_id

              #Add route for leaf on spine only if dhcp_flag is true
              if (dhcp_flag):
                  route_cmd_arg=" route_cmd=\"add "+network_id+ " via "+leaf_ip+"\""
                  extra_vars=constants.ansible_become_pass+ns_name_arg+route_cmd_arg+ " " + hypervisor_arg
                  raas_utils.run_shell_script("ansible-playbook logic/misc/add_route_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
             
              route_cmd_arg = " route_cmd= \"add "+t_loopback_ip+" via " + leaf_ip+"\""
              extra_vars=constants.ansible_become_pass+ns_name_arg+route_cmd_arg+ " " + hypervisor_arg
              raas_utils.run_playbook("ansible-playbook logic/misc/add_route_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")

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
          raas_utils.log_service(route_weight)

          route_cmd_arg=" route_cmd="+route_weight
          extra_vars=constants.ansible_become_pass+ns_name_arg+route_cmd_arg+ " " + hypervisor_arg
          raas_utils.run_shell_script("ansible-playbook logic/misc/add_route_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
    
        except Exception as e:
            raas_utils.log_service("Connecting leaf to spines failed: "+str(e))
            raise

        hyp_utils.write_leaf_id(lid+1, vpc_name, hypervisor)
        hyp_utils.vpc_add_leaf(hypervisor, vpc_name, leaf_name, leaf_name_hyp)
        raas_utils.client_add_leaf(hypervisor, vpc_name, leaf_name, network_id)

    except Exception as e:
        extra_vars=constants.ansible_become_pass + " " + leaf_name_hyp_arg +  " " + hypervisor_arg
        raas_utils.run_shell_script("ansible-playbook logic/misc/delete_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
