---
- name: Create network namespace with a bridge
  hosts: [localhost]
  user: root
  become: yes
  vars:
    ansible_python_interpreter: /usr/bin/python3
    
  tasks:
          #- name: Create network namespace
          #command: "ip netns add {{b_name}}"
          #ignore_errors: yes

    - name: Create bridge in namespace
      command: "ip netns exec {{b_name}} brctl addbr {{b_name}}_br"
      ignore_errors: yes

    - name: Up the bridge
      command: "ip netns exec {{b_name}} ip link set {{b_name}}_br up"
      ignore_errors: yes

      #- name: Create veth pair
      #command: "ip link add {{b_name}}_{{l_name}} type veth peer name {{l_name}}_{{b_name}}"
      #ignore_errors: yes

      #- name: Add veth endpoint1 to namespace
      #command: "ip link set {{b_name}}_{{l_name}} netns {{b_name}}"
      #ignore_errors: yes
    
      #- name: Up endpoint1
      #command: "ip netns exec {{b_name}} ip link set {{b_name}}_{{l_name}} up"
      #ignore_errors: yes

      #- name: Link endpoint1 to internal bridge
      #command: "ip netns exec {{b_name}} brctl addif {{b_name}}_br {{b_name}}_{{l_name}}"
      #ignore_errors: yes

      #- name: Add veth endpoint2 to leaf container
      #command: "ip link set {{l_name}}_{{b_name}} netns {{l_name}}"
      #ignore_errors: yes
    
      #- name: Up endpoint2
      #command: "ip netns exec {{l_name}} ip link set {{l_name}}_{{b_name}} up"
      #ignore_errors: yes

    - name: Assign IP for dhcp server
      command: "ip netns exec {{b_name}} ip addr add {{ip}} dev {{b_name}}_br"
      ignore_errors: yes
      when: ip is defined and range is defined

    - name: Create DHCP server for the bridge namespace
      command: "ip netns exec {{b_name}} dnsmasq --interface={{b_name}}_br --dhcp-range={{ range }},12h --bind-interfaces --except-interface=lo"
      ignore_errors: yes
      when: ip is defined and range is defined
