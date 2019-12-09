import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress

"""@params:
    param1 = connection config name (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give connection config file")
        exit(1)

    connection_config_file = sys.argv[1]
    connection_name = connection_config_file.split('/')[-1].split('.')[0]
    cid = hyp_utils.get_client_id()

    connection_data = do_json.json_read(connection_config_file)
    print(connection_data)

    # hypervisor = connection_data["hypervisor_name"]
    # hypervisor_arg = "hypervisor="+hypervisor
    # hypervisors_data = hyp_utils.get_hypervisors_data()
    # hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)
    
    cid = hyp_utils.get_client_id()

    l1_transit_name = connection_data["l1_transit_name"]
    l2_transit_name = connection_data["l2_transit_name"]

    l1_transit_hypervisor_name = connection_data["l1_transit_hypervisor_name"]
    l2_transit_hypervisor_name = connection_data["l2_transit_hypervisor_name"]

    if (l1_transit_hypervisor_name == l2_transit_hypervisor_name):
        #connect l1 transit to l2 transit local
        try:
            hypervisor = connection_data["hypervisor_name"]
            hypervisor_arg = "hypervisor="+hypervisor
            hypervisors_data = hyp_utils.get_hypervisors_data()
            hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)
        except Exception as e:
            print("l1 transit to l2 transit local failed",e)
            raise
    else:
        print("l1 and l2 transits exist in different hypervisor, GRE connect")
        exit(1)

