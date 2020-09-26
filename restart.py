import urllib.request
import json
import os
import pickle
from wallet import Wallet


def bootstrap(address, seeds):
    data = {
        "seeds": seeds
    }
    req = urllib.request.Request("http://" + address + "/bootstrap",
                          bytes(json.dumps(data),'utf8'),
                          {"Content-Type": "application/json"})
    res_data = urllib.request.urlopen(req)
    res = res_data.read().decode('utf8')
    return res

def bootstrap2(address, seeds):
    data = {
        "seeds": seeds
    }
    req = urllib.request.Request("http://" + address + "/bootstrap2",
                          bytes(json.dumps(data),'utf8'),
                          {"Content-Type": "application/json"})
    res_data = urllib.request.urlopen(req)
    res = res_data.read().decode('utf8')
    return res

def get_node_info(address):
    req = urllib.request.Request(url="http://" + address + "/curr_node",
                          headers={"Content-Type": "application/json"})

    res_data = urllib.request.urlopen(req)
    res = res_data.read().decode('utf8')
    return json.loads(res)


from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
args = parser.parse_args()
port = args.port

if port == 5000:
    genisus_node = True
else:
    genisus_node = False

tmp = Wallet(genisus_node, port)
address = tmp.address

if os.path.exists(address):
    print('---restart---')
    
    info = get_node_info("127.0.0.1:"+str(port))
    with open(address+'/seeds.data', 'rb') as f:
        seeds = pickle.load(f)
    print("seeds :", seeds)
    bootstrap2("127.0.0.1:"+str(port), seeds)
