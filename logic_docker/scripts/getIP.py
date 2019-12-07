#!/bin/bash
import os

if __name__ == "__main__":
    vm_name = str(sys.argv[1])
    mgmt_name="mns1"
    os.system("docker inspect "+vm_name+" -f {{.NetworkSettings.Networks."+mgmt_name+".IPAddress}}")