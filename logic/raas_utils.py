import sys
import do_json
import constants
import os

def get_mgmt_nid():
    json_data = do_json.json_read(constants.mgmt_net_file)
    return json_data["network_id"]

def client_exists_vpc(vpc_name):
    return os.path.exists(constants.var_vpc + vpc_name + "/" + vpc_name)

def client_add_vpc(vpc_name):
    vpc_dir = constants.var_vpc + vpc_name + "/"

    if not os.path.exists(vpc_dir):
        os.makedirs(vpc_dir)

    with open(vpc_dir + vpc_name, "w") as f:
        f.write(vpc_name)

    vpc_spines_dir = vpc_dir + constants.vpc_spines
    if not os.path.exists(vpc_spines_dir):
        os.makedirs(vpc_spines_dir)

    vpc_leafs_dir = vpc_dir + constants.vpc_leafs
    if not os.path.exists(vpc_leafs_dir):
        os.makedirs(vpc_leafs_dir)

    vpc_bridges_dir = vpc_dir + constants.vpc_bridges
    if not os.path.exists(vpc_bridges_dir):
        os.makedirs(vpc_bridges_dir)

    vpc_pcs_dir = vpc_dir + constants.vpc_pcs
    if not os.path.exists(vpc_pcs_dir):
        os.makedirs(vpc_pcs_dir)

def client_exists_spine(vpc_name, spine_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_spines + spine_name

    return os.path.exists(file_path)

def client_add_spine(vpc_name, spine_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_spines + spine_name
    with open(file_path, "w") as f:
        f.write(spine_name)

def client_exists_pc(vpc_name, pc_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_pcs + pc_name

    return os.path.exists(file_path)

def client_add_pc(vpc_name, pc_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_pcs + pc_name
    with open(file_path, "w") as f:
        f.write(pc_name)

#def client_exists_bridge(vpc_name, bridge_name):
#    file_path = constants.var_vpc + vpc_name + \
#            constants.vpc_bridges + bridge_name
#
#    return os.path.exists(file_path)
#
#def client_add_bridge(vpc_name, bridge_name):
#    file_path = constants.var_vpc + vpc_name + \
#            constants.vpc_bridges + bridge_name
#    with open(file_path, "w") as f:
#        f.write(bridge_name)

