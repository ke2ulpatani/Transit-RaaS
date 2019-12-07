import json

def json_read(json_file):
    with open(json_file) as f:
        data = json.load(f)
    return data

def json_write(data, json_file):
    with open(json_file, "w") as f:
        json.dump(data, f)
