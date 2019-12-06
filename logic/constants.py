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

ansible_become_pass="ansible_become_pass=yashrocks"

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
img_path="/var/lib/libvirt/images/"
spine_vm_img="routerVM.img"
#1g_mem = 976562
#2g_mem = 1953125
#4g_mem = 3906250
