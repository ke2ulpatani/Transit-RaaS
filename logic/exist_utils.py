import sys
import do_json
import constants

def exists_mgmt_ns():
    json_data = do_json.json_read(constants.metadata_file) 
    if "nsm" not in json_data:
        return False 

    return True

def get_client_id():
    with open(constants.cid_file) as f:
        cid = f.readline()

    return cid

def get_mgmt_nid():
    with open(constants.mgmt_net_file) as f:
        json_data = do_json.json_read(f)
    
    return json_data["network_id"]

def get_new_br():
    with open(constants.brid_file, "w") as f:
        brid = f.readline()
        f.truncate()
        f.write(int(brid)+1)

    return brid

def get_h_nsm_ip(hypervisor):
    filename = "constants."+hypervisor+"_nsm_ip_file"
    with open(filename) as f:
        ip = f.readline()

    return ip

def get_nsm_h_ip(hypervisor):
    filename = "constants.nsm_"+hypervisor+"_ip_file"
    with open(filename) as f:
        ip = f.readline()

    return ip
