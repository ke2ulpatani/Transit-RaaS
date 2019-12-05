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

metadata_file="../var/metadata.json"
cid_file="../var/cid"
mgmt_net_file = "../etc/networks/mgmt_net.json"
hypervisors_file = "../etc/misc/hypervisors.json"
brid_file="../var/brid"
h1_nsm_ip_file="../var/h1_nsm_ip"
nsm_h1_ip_file="../var/nsm_h1_ip"
h2_nsm_ip_file="../var/h2_nsm_ip"
nsm_h2_ip_file="../var/nsm_h2_ip"

