
def client_exists_leaf(vpc_name, leaf_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_leafs + leaf_name

    return os.path.exists(file_path)

def client_add_leaf(vpc_name, leaf_name):
    file_path = constants.var_vpc + vpc_name + \
            constants.vpc_leafs + leaf_name
    with open(file_path, "w") as f:
        f.write(leaf_name)
