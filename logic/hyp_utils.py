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

def get_leafs_data(hypervisor, vpc):
    vpc_data = get_vpc_data(hypervisor, vpc)
    leafs_data = vpc_data["leaf"]
    return leafs_data

def write_leafs_data(leafs_data, vpc, hypervisor):
    vpc_data = get_vpc_data(hypervisor, vpc)
    vpc_data["leaf"] = leafs_data
    write_vpc_data(vpc_data, vpc, hypervisor)

def get_leaf_data(hypervisor, vpc, leaf):
    leafs_data = get_leafs_data(hypervisor, vpc)
    leaf_data = leafs_data[leaf]
    return leaf_data

def write_leaf_data(leaf_data, leaf, vpc, hypervisor):
    leafs_data = get_leafs_data(hypervisor, vpc)
    leafs_data[leaf] = leaf_data
    write_leafs_data(leafs_data, vpc, hypervisor)

def get_leaf_id(hypervisor, vpc):
    leafs_data = get_leafs_data(hypervisor, vpc)
    leaf_id = int(leafs_data["id"])
    return leaf_id

def write_leaf_id(leaf_id, vpc, hypervisor):
    leafs_data = get_leafs_data(hypervisor, vpc)
    leafs_data["id"] = str(leaf_id)
    write_leafs_data(leafs_data, vpc, hypervisor)

def get_pcs_data(hypervisor, vpc):
    vpc_data = get_vpc_data(hypervisor, vpc)
    pcs_data = vpc_data["pc"]
    return pcs_data

def write_pcs_data(pcs_data, vpc, hypervisor):
    vpc_data = get_vpc_data(hypervisor, vpc)
    vpc_data["pc"] = pcs_data
    write_vpc_data(vpc_data, vpc, hypervisor)

def get_pc_data(hypervisor, vpc, pc):
    pcs_data = get_pcs_data(hypervisor, vpc)
    pc_data = pcs_data[pc]
    return pc_data

def write_pc_data(pc_data, pc, vpc, hypervisor):
    pcs_data = get_pcs_data(hypervisor, vpc)
    pcs_data[pc] = pc_data
    write_pcs_data(pcs_data, vpc, hypervisor)

def get_pc_id(hypervisor, vpc):
    pcs_data = get_pcs_data(hypervisor, vpc)
    pc_id = int(pcs_data["id"])
    return pc_id

def write_pc_id(pc_id, vpc, hypervisor):
    pcs_data = get_pcs_data(hypervisor, vpc)
    pcs_data["id"] = str(pc_id)
    write_pcs_data(pcs_data, vpc, hypervisor)

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

    new_spines_data = {}
    write_spines_data(new_spines_data, cust_vpc_name, hypervisor)
    new_spine_id = "1"
    write_spine_id(new_spine_id, cust_vpc_name, hypervisor)

    new_leafs_data = {}
    write_leafs_data(new_leafs_data, cust_vpc_name, hypervisor)
    new_leaf_id = "1"
    write_leaf_id(new_leaf_id, cust_vpc_name, hypervisor)

    new_pcs_data = {}
    write_pcs_data(new_pcs_data, cust_vpc_name, hypervisor)
    new_pc_id = "1"
    write_pc_id(new_pc_id, cust_vpc_name, hypervisor)

def get_hyp_spine_name(hypervisor, vpc, spine):
    spine_data = get_spine_data(hypervisor, vpc, spine)
    hyp_spine_name = spine_data["name"]
    return hyp_spine_name

def write_hyp_spine_name(hyp_spine_name, spine, vpc, hypervisor):
    spine_data = get_spine_data(hypervisor, vpc, spine)
    spine_data["name"] = hyp_spine_name 
    write_spine_data(spine_data, spine, vpc, hypervisor)

def vpc_add_spine(hypervisor, vpc, cust_spine_name, hyp_spine_name):
    new_spine_data = {}
    write_spine_data(new_spine_data, cust_spine_name, vpc, hypervisor)
    write_hyp_spine_name(hyp_spine_name, cust_spine_name, vpc, hypervisor)

def get_hyp_leaf_name(hypervisor, vpc, leaf):
    leaf_data = get_leaf_data(hypervisor, vpc, leaf)
    hyp_leaf_name = leaf_data["name"]
    return hyp_leaf_name

def write_hyp_leaf_name(hyp_leaf_name, leaf, vpc, hypervisor):
    leaf_data = get_leaf_data(hypervisor, vpc, leaf)
    leaf_data["name"] = hyp_leaf_name 
    write_leaf_data(leaf_data, leaf, vpc, hypervisor)

def vpc_add_leaf(hypervisor, vpc, cust_leaf_name, hyp_leaf_name):
    new_leaf_data = {}
    write_leaf_data(new_leaf_data, cust_leaf_name, vpc, hypervisor)
    write_hyp_leaf_name(hyp_leaf_name, cust_leaf_name, vpc, hypervisor)

def get_hyp_pc_name(hypervisor, vpc, pc):
    pc_data = get_pc_data(hypervisor, vpc, pc)
    hyp_pc_name = pc_data["name"]
    return hyp_pc_name

def write_hyp_pc_name(hyp_pc_name, pc, vpc, hypervisor):
    pc_data = get_pc_data(hypervisor, vpc, pc)
    pc_data["name"] = hyp_pc_name 
    write_pc_data(pc_data, pc, vpc, hypervisor)

def vpc_add_pc(hypervisor, vpc, cust_pc_name, hyp_pc_name):
    new_pc_data = {}
    write_pc_data(new_pc_data, cust_pc_name, vpc, hypervisor)
    write_hyp_pc_name(hyp_pc_name, cust_pc_name, vpc, hypervisor)
