import sys
import do_json
import constants

def exists_mgmt_ns(hypervisor):
    json_data = do_json.json_read(constants.hypervisors_file) 
    if json_data[hypervisor]["nsm_exists"] == "False":
        return False 

    return True

def add_mgmt_ns(hypervisor):
    json_data = do_json.json_read(constants.hypervisors_file) 
    json_data[hypervisor]["nsm_exists"] = "True"
    do_json.json_write(json_data, constants.hypervisors_file)

def get_client_id():
    with open(constants.cid_file) as f:
        cid = f.readline()

    return cid

def get_mgmt_nid():
    json_data = do_json.json_read(constants.mgmt_net_file)
    return json_data["network_id"]

def get_new_br():
    with open(constants.brid_file, "w") as f:
        brid = f.readline()
        f.truncate()
        f.write(int(brid)+1)

    return brid

def get_h_nsm_ip(hypervisor):
    json_data = do_json.json_read(constants.hypervisors_file)
    return json_data[hypervisor]["h_nsm_ip"]

def get_nsm_h_ip(hypervisor):
    json_data = do_json.json_read(constants.hypervisors_file)
    return json_data[hypervisor]["nsm_h_ip"]
