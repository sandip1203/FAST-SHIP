import json 

def read_data():
    with open("data.json","r") as data_file:
        data = json.load(data_file)
    return data
    
def write_data(data_json):
    with open("data.json","w") as data_file:
        data = json.dump(data_json,data_file)
    return data