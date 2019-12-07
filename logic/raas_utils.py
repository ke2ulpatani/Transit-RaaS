import sys
import do_json
import constants
import os
from os import listdir
from os.path import isfile, join

def get_mgmt_nid():
    json_data = do_json.json_read(constants.mgmt_net_file)
    return json_data["network_id"]

def client_exists_vpc(vpc_name):
    return os.path.exists(constants.var_vpc + vpc_name + "/" + vpc_name + ".json")

def client_add_vpc(vpc_name):
    vpc_dir = constants.var_vpc + vpc_name + "/"
    file_path = vpc_dir + vpc_name + ".json"

    if not os.path.exists(vpc_dir):
        os.makedirs(vpc_dir)

    new_vpc_data = {"name": vpc_name}
    do_json.json_write(new_vpc_data, file_path)

    vpc_spines_dir = vpc_dir + constants.vpc_spines
    if not os.path.exists(vpc_spines_dir):
        os.makedirs(vpc_spines_dir)

    vpc_leafs_dir = vpc_dir + constants.vpc_leafs
    if not os.path.exists(vpc_leafs_dir):
        os.makedirs(vpc_leafs_dir)

    vpc_pcs_dir = vpc_dir + constants.vpc_pcs
    if not os.path.exists(vpc_pcs_dir):
        os.makedirs(vpc_pcs_dir)

def client_exists_spine(vpc_name, spine_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_spines + spine_name+ ".json"

    return os.path.exists(file_path)

def client_add_spine(vpc_name, spine_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_spines + spine_name + ".json"

    new_spine_data = {"name": spine_name}
    do_json.json_write(new_spine_data, file_path)

def client_exists_leaf(vpc_name, leaf_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_leafs + leaf_name + ".json"

    return os.path.exists(file_path)

def get_all_spines(vpc_name):
    dir_path=constants.var_vpc + vpc_name + \
            constants.vpc_spines
    spines = [f.split('.')[0] for f in listdir(dir_path) if isfile(join(dir_path, f))]
    print(spines)


def client_add_leaf(vpc_name, leaf_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_leafs + leaf_name + ".json"
    new_leaf_data = {"name": leaf_name}
    do_json.json_write(new_leaf_data, file_path)

def client_exists_pc(vpc_name, pc_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_pcs + pc_name + ".json"

    return os.path.exists(file_path)

def client_add_pc(vpc_name, pc_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_pcs + pc_name + ".json"
    new_pc_data = {"name": pc_name}
    do_json.json_write(new_pc_data, file_path)

def write_spine_ip(vpc, spine, spine_ip):
    file_path = constants.var_vpc + vpc + \
            constants.vpc_spines + spine + ".json"

    spine_data = do_json.json_read(file_path)
    spine_data["ip"] = spine_ip
    do_json.json_write(spine_data, file_path)

def get_spine_ip(vpc, spine):
    file_path = constants.var_vpc + vpc + \
            constants.vpc_spines + spine + ".json"
    spine_data = do_json.json_read(file_path)
    spine_ip = spine_data["ip"]
    return spine_ip

def read_temp_file():
    with open(constants.temp_file) as f:
        data = f.read()

    return data

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

