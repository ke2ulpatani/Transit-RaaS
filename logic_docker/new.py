
def get_hyp_l1_transit_name(hypervisor, l1_transit):
    l1_transit_data = get_l1_transit_data(hypervisor, l1_transit)
    hyp_l1_transit_name = l1_transit_data["name"]
    return hyp_l1_transit_name

def write_hyp_l1_transit_name(hyp_l1_transit_name, l1_transit, hypervisor):
    l1_transit_data = get_l1_transit_data(hypervisor, l1_transit)
    l1_transit_data["name"] = hyp_l1_transit_name
    write_l1_transit_data(l1_transit_data, l1_transit, hypervisor)

def hyp_add_l1_transit(hypervisor, cust_l1_transit_name, hyp_l1_transit_name):
    new_l1_transit_data = {}
    write_l1_transit_data(new_l1_transit_data, cust_l1_transit_name, hypervisor)
    write_hyp_l1_transit_name(hyp_l1_transit_name, cust_l1_transit_name, hypervisor)

    new_spines_data = {}
    write_spines_data(new_spines_data, cust_l1_transit_name, hypervisor)
    new_spine_id = "1"
    write_spine_id(new_spine_id, cust_l1_transit_name, hypervisor)

    new_leafs_data = {}
    write_leafs_data(new_leafs_data, cust_l1_transit_name, hypervisor)
    new_leaf_id = "1"
    write_leaf_id(new_leaf_id, cust_l1_transit_name, hypervisor)

    new_pcs_data = {}
    write_pcs_data(new_pcs_data, cust_l1_transit_name, hypervisor)
    new_pc_id = "1"
    write_pc_id(new_pc_id, cust_l1_transit_name, hypervisor)
