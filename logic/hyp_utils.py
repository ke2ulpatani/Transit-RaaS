import sys
import do_json
import constants
import os

def get_client_id():
    hypervisors_data = do_json.json_read(constants.hypervisors_file)
    return hypervisors_data["customer_id"]

def get_hypervisors_data():
    hypervisors_data = do_json.json_read(constants.hypervisors_file)
    return hypervisors_data

def write_hypervisors_data(hypervisors_data):
    do_json.json_write(hypervisors_data, constants.hypervisors_file)

def get_hyp_data(hypervisor):
    hypervisors_data = get_hypervisors_data()
    hyp_data = hypervisors_data[hypervisor]
    return hyp_data

def write_hyp_data(hyp_data, hypervisor):
    hypervisors_data = get_hypervisors_data()
    hypervisors_data[hypervisor] = hyp_data
    write_hypervisors_data(hypervisors_data)

def get_hyp_ip(hypervisor):
    hyp_data = get_hyp_data(hypervisor)

    if hyp_data == None:
        print("Hypervisor does not exist")
        return None

    hypervisor_ip = hyp_data["ip"]
    return hypervisor_ip

def exists_mgmt_ns(hypervisor):
    hyp_data = get_hyp_data(hypervisor)
    if hyp_data["nsm_exists"] == "True":
        return True

    return False

def add_mgmt_ns(hypervisor):
    hyp_data = get_hyp_data(hypervisor)
    hyp_data["nsm_exists"] = "True"
    write_hyp_data(hyp_data, hypervisor)

def get_mgmt_net(cid):
    return "c"+cid+"_m_net"

def get_nsm_br(hypervisor):
    hyp_data = get_hyp_data(hypervisor)
    nsm_br = hyp_data["nsm_br"]
    return nsm_br

def add_nsm_br(br_name, hypervisor):
    hyp_data = get_hyp_data(hypervisor)
    hyp_data["nsm_br"] = br_name
    write_hyp_data(hyp_data, hypervisor)

def get_h_nsm_ip(hypervisor):
    hyp_data = get_hyp_data(hypervisor)
    return hyp_data["h_nsm_ip"]

def get_nsm_h_ip(hypervisor):
    hyp_data = get_hyp_data(hypervisor)
    return hyp_data["nsm_h_ip"]

def get_vpcs_data(hypervisor):
    hyp_data = get_hyp_data(hypervisor)
    vpcs_data = hyp_data["vpc"]
    return vpcs_data

def write_vpcs_data(vpcs_data, hypervisor):
    hyp_data = get_hyp_data(hypervisor)
    hyp_data["vpc"] = vpcs_data
    write_hyp_data(hyp_data, hypervisor)

def get_vpc_data(hypervisor, vpc):
    vpcs_data = get_vpcs_data(hypervisor)
    return vpcs_data[vpc]

def write_vpc_data(vpc_data, vpc, hypervisor):
    vpcs_data = get_vpcs_data(hypervisor)
    vpcs_data[vpc] = vpc_data
    write_vpcs_data(vpcs_data, hypervisor)

def get_vpc_id(hypervisor):
    vpcs_data = get_vpcs_data(hypervisor)
    vpc_id = int(vpcs_data["id"])
    return vpc_id

def write_vpc_id(vpc_id, hypervisor):
    vpcs_data = get_vpcs_data(hypervisor)
    vpcs_data["id"] = str(vpc_id)
    write_vpcs_data(vpcs_data, hypervisor)

def get_spines_data(hypervisor, vpc):
    vpc_data = get_vpc_data(hypervisor, vpc)
    spines_data = vpc_data["spine"]
    return spines_data

def write_spines_data(spines_data, vpc, hypervisor):
    vpc_data = get_vpc_data(hypervisor, vpc)
    vpc_data["spine"] = spines_data
    write_vpc_data(vpc_data, vpc, hypervisor)

def get_spine_data(hypervisor, vpc, spine):
    spines_data = get_spines_data(hypervisor, vpc)
    spine_data = spines_data[spine]
    return spine_data

def write_spine_data(spine_data, spine, vpc, hypervisor):
    spines_data = get_spines_data(hypervisor, vpc)
    spines_data[spine] = spine_data
    write_spines_data(spines_data, vpc, hypervisor)

def get_spine_id(hypervisor, vpc):
    spines_data = get_spines_data(hypervisor, vpc)
    spine_id = int(spines_data["id"])
    return spine_id

def write_spine_id(spine_id, vpc, hypervisor):
    spines_data = get_spines_data(hypervisor, vpc)
    spines_data["id"] = str(spine_id)
    write_spines_data(spines_data, vpc, hypervisor)

def get_bridges_data(hypervisor, vpc):
    vpc_data = get_vpc_data(hypervisor, vpc)
    bridges_data = vpc_data["bridges"]
    return bridgess_data

def write_bridges_data(bridges_data, vpc, hypervisor):
    vpc_data = get_vpc_data(hypervisor, vpc)
    vpc_data["bridges"] = bridges_data
    write_vpc_data(vpc_data, vpc, hypervisor)

def get_bridge_data(hypervisor, vpc, bridge):
    bridges_data = get_bridges_data(hypervisor, vpc)
    bridge_data = bridges_data[bridge]
    return bridge_data

def write_bridge_data(bridge_data, bridge, vpc, hypervisor):
    bridges_data = get_bridges_data(hypervisor, vpc)
    bridges_data[spine] = bridge_data
    write_bridges_data(bridges_data, vpc, hypervisor)

def get_bridge_id(hypervisor, vpc):
    bridges_data = get_bridges_data(hypervisor, vpc)
    bridge_id = int(bridges_data["id"])
    return bridges_id

def write_bridge_id(bridge_id, vpc, hypervisor):
    bridges_data = get_bridges_data(hypervisor, vpc)
    bridges_data["id"] = str(bridge_id)
    write_bridges_data(bridges_data, vpc, hypervisor)

def get_hyp_vpc_name(hypervisor, vpc):
    vpc_data = get_vpc_data(hypervisor, vpc)
    hyp_vpc_name = vpc_data["name"]
    return hyp_vpc_name

def write_hyp_vpc_name(hyp_vpc_name, vpc, hypervisor):
    vpc_data = get_vpc_data(hypervisor, vpc)
    vpc_data["name"] = hyp_vpc_name
    write_vpc_data(vpc_data, vpc, hypervisor)

def hyp_add_vpc(hypervisor, cust_vpc_name, hyp_vpc_name):
    new_vpc_data = {}
    write_vpc_data(new_vpc_data, cust_vpc_name, hypervisor)
    write_hyp_vpc_name(hyp_vpc_name, cust_vpc_name, hypervisor)
