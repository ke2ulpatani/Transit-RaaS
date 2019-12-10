"""
Identifiers:
hypervisor: h
customer: c
vpc: v
spine: s
l1transit: t1
l2transit: t2
leaf: l
vm: vm
namespace: ns
veth: ve_d1_d2 (d1->d2)
bridge: b
network: net
subnet: nid
manamgement: m
management namespace: nsm
"""
client_log_file = "client.log"
service_log_file = "service.log"
ssh_file = "~/.ssh/id_raas"
ansible_become_pass="ansible_ssh_pass=yashrocks ansible_become_pass=yashrocks"
ansible_ssh_private_key_file="ansible_ssh_private_key_file="+ssh_file

#etc
mgmt_net_file = "etc/networks/mgmt_net.json"

#var
metadata_file="var/metadata.json"
cid_file="var/cid"
hypervisors_file = "var/hypervisors.json"
brid_file="var/brid"
sid_file="var/sid" #spine id file
h1_nsm_ip_file="var/h1_nsm_ip"
nsm_h1_ip_file="var/nsm_h1_ip"
h2_nsm_ip_file="var/h2_nsm_ip"
nsm_h2_ip_file="var/nsm_h2_ip"
var_vpc="var/vpc/"
vpc_spines="/spines/"
l1_transits="var/l1_transits/"
l2_transits="var/l2_transits/"
vpc_leafs="/leafs/"
vpc_bridges="/bridges/"
vpc_pcs="/pcs/"
img_path="/var/lib/libvirt/images/"
spine_vm_img="routerVM.img"
pc_vm_img="sampleBuild.img"
l1_transit_vm_img="routerVM.img"
l2_transit_vm_img="routerVM.img"
var_spines="/var/spines/"
f1_mem = 976562
f2_mem = 1953125
f3_mem = 3906250
temp_file = "var/temp"
new_mgmt_net_data = {
    "hypervisor_name" : "",
    "network_id" : "",
    "subnet_name" : ""
}
new_vpc_data = {
    "hypervisor_name": "",
    "vpc_name": ""
}
new_vpc_data["peering"] = False

new_pc_data = {
    "hypervisor_name":"",
    "vpc_name":"",
    "pc_name": "",
    "capacity":""
}
new_pc_data["leafs"]=[]

new_leaf_data = {
    "hypervisor_name" : "",
    "network_id" : "",
    "leaf_name" : "",
    "vpc_name": ""
}
new_spine_data = {
    "hypervisor_name" : "",
    "spine_name" : "",
    "vpc_name": "",
    "capacity": ""
}
new_l1_transit_data = {
    "hypervisor_name" :"",
    "l1_transit_name" :"",
    "capacity": ""
}
new_l2_transit_data = {
    "hypervisor_name" :"",
    "l2_transit_name" :"",
    "capacity": ""
}
