# coding:utf-8
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.utils import old_div
import json
import random
import time
import urllib.request, urllib.error, urllib.parse
import pickle


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


def run():
    node = list()
    for i in range(5):
        node.append(get_node_info("127.0.0.1:500" + str(i)))
        print('node', i+1)
    seeds = [
        {"node_id": node[i]["node_id"], "ip": node[i]["ip"], "port": node[i]["port"]} for i in range(5)
    ]
    for i in range(5):
        tmp = seeds[0]
        del seeds[0]
        bootstrap("127.0.0.1:500"+str(i), seeds)
        with open(node[i]["wallet"]+'/seeds.data', 'wb') as f:
            pickle.dump(seeds, f)       
        seeds.append(tmp)
    print("ok")
    time.sleep(1)

    node1_wallet = node[0]["wallet"]
    node2_wallet = node[1]["wallet"]
    node3_wallet = node[2]["wallet"]
    node4_wallet = node[3]["wallet"]
    node5_wallet = node[4]["wallet"]

    
    while True:
        # node1 发送给node2 node3
        amount = random.randint(1, 10)
        print('send from node1 to node2 with amount:'+str(amount))
        simulate_tx("127.0.0.1:5000", node1_wallet, node2_wallet, amount)
        time.sleep(random.randint(1,2))

        amount = random.randint(1, 10)
        print('send from node1 to node3 with amount:' + str(amount))
        simulate_tx("127.0.0.1:5000", node1_wallet, node3_wallet, amount)
        time.sleep(random.randint(1,2))

        # node2 发送给node1 node3
        amount = random.randint(1, 10)
        print('send from node2 to node1 with amount:' + str(amount))
        simulate_tx("127.0.0.1:5001", node2_wallet, node1_wallet, amount)
        time.sleep(random.randint(1,2))

        amount = random.randint(1, 10)
        print('send from node2 to node3 with amount:' + str(amount))
        simulate_tx("127.0.0.1:5001", node2_wallet, node3_wallet, amount)
        time.sleep(random.randint(1,2))
        
        # node3 发送给node1 node2
        amount = random.randint(1, 10)
        print('send from node3 to node1 with amount:' + str(amount))
        simulate_tx("127.0.0.1:5002", node3_wallet, node1_wallet, amount)
        time.sleep(random.randint(1,2))

        amount = random.randint(1, 10)
        print('send from node3 to node2 with amount:' + str(amount))
        simulate_tx("127.0.0.1:5002", node3_wallet, node2_wallet, amount)
        time.sleep(random.randint(1,2))
        
        time.sleep(1)


def simulate_tx(address, sender, receiver, amount):
    data = {
        "sender": sender,
        "receiver": receiver,
        "amount": amount
    }

    req = urllib.request.Request(url="http://" + address + "/transactions/new_easy",
                          headers={"Content-Type": "application/json"}, data=bytes(json.dumps(data),'utf8'))
    res_data = urllib.request.urlopen(req)
    res = res_data.read().decode('utf8')
    return res


def get_balance(address, wallet_addres):
    req = urllib.request.Request(url="http://" + address + "/balance?address=" + wallet_addres,
                          headers={"Content-Type": "application/json"})

    res_data = urllib.request.urlopen(req)
    res = res_data.read().decode('utf8')
    return json.loads(res)


def get_node_info(address):
    req = urllib.request.Request(url="http://" + address + "/curr_node",
                          headers={"Content-Type": "application/json"})

    res_data = urllib.request.urlopen(req)
    res = res_data.read().decode('utf8')
    return json.loads(res)


run()
