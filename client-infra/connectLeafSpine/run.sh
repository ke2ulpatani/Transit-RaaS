for entry in "leaf"/*
do
  ansible-playbook connectLeafSpine.yml --extra-vars "@$entry"
done

