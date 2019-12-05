for entry in "leaf"/*
do
  ansible-playbook -i ./inventory/hosts.yml connectLeafSpine.yml --extra-vars "@$entry" -vv
done

