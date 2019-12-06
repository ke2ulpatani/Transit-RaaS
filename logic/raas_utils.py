import sys
import do_json
import constants
import os

def get_mgmt_nid():
    json_data = do_json.json_read(constants.mgmt_net_file)
    return json_data["network_id"]

def client_exists_vpc(vpc_name):
    return os.path.exists(var_vpc + vpc_name)

def client_add_vpc(vpc_name):
    with open(var_vpc + vpc_name, "w") as f:
        f.write(vpc_name)
