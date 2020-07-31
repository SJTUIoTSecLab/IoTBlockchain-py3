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
    node1 = get_node_info("127.0.0.1:5000")
    node2 = get_node_info("127.0.0.1:5001")
    node3 = get_node_info("127.0.0.1:5002")

    node1_seeds = [
        {"node_id": node2["node_id"], "ip": node2["ip"], "port": node2["port"]},
        {"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]}
    ]
    print(node1_seeds)
    bootstrap("127.0.0.1:5000", node1_seeds)

    node2_seeds = [
        {"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]},
        {"node_id": node1["node_id"], "ip": node1["ip"], "port": node1["port"]}
    ]
    bootstrap("127.0.0.1:5001", node2_seeds)

    node3_seeds = [
        {"node_id": node1["node_id"], "ip": node1["ip"], "port": node1["port"]},
        {"node_id": node2["node_id"], "ip": node2["ip"], "port": node2["port"]}
    ]
    bootstrap("127.0.0.1:5002", node3_seeds)
    print("ok")
    time.sleep(1)

    node1_wallet = node1["wallet"]
    node2_wallet = node2["wallet"]
    node3_wallet = node3["wallet"]
    
    while True:
        # node1 发送给node2 node3
        node1_balance = get_balance("127.0.0.1:5000", node1_wallet)
        node1_balance = node1_balance['balance']
        if node1_balance > 0:
            amount = old_div(random.randint(1, node1_balance),10)
            print('send from node1 to node2 with amount:'+str(amount))
            simulate_tx("127.0.0.1:5000", node1_wallet, node2_wallet, amount)
            time.sleep(random.randint(4,5))

        node1_balance = get_balance("127.0.0.1:5000", node1_wallet)
        node1_balance = node1_balance['balance']
        if node1_balance > 0:
            amount = old_div(random.randint(1, node1_balance),10)
            print('send from node1 to node3 with amount:' + str(amount))
            simulate_tx("127.0.0.1:5000", node1_wallet, node3_wallet, amount)
            time.sleep(random.randint(4,5))

        # node2 发送给node1 node3
        node2_balance = get_balance("127.0.0.1:5001", node2_wallet)
        node2_balance = node2_balance['balance']
        if node2_balance > 0:
            amount = old_div(random.randint(1, node2_balance),10)
            print('send from node2 to node1 with amount:' + str(amount))
            simulate_tx("127.0.0.1:5001", node2_wallet, node1_wallet, amount)
            time.sleep(random.randint(4,5))

        node2_balance = get_balance("127.0.0.1:5001", node2_wallet)
        node2_balance = node2_balance['balance']
        if node2_balance > 0:
            amount = old_div(random.randint(1, node2_balance),10)
            print('send from node2 to node3 with amount:' + str(amount))
            simulate_tx("127.0.0.1:5001", node2_wallet, node3_wallet, amount)
            time.sleep(random.randint(4,5))
        #
        # node3 发送给node1 node2
        node3_balance = get_balance("127.0.0.1:5002", node3_wallet)
        node3_balance = node3_balance['balance']
        if node3_balance > 0:
            amount = old_div(random.randint(1, node3_balance),10)
            print('send from node3 to node1 with amount:' + str(amount))
            simulate_tx("127.0.0.1:5002", node3_wallet, node1_wallet, amount)
            time.sleep(random.randint(4,5))

        node3_balance = get_balance("127.0.0.1:5002", node3_wallet)
        node3_balance = node3_balance['balance']
        if node3_balance > 0:
            amount = old_div(random.randint(1, node3_balance),10)
            print('send from node3 to node2 with amount:' + str(amount))
            simulate_tx("127.0.0.1:5002", node3_wallet, node2_wallet, amount)
            time.sleep(random.randint(4,5))
        time.sleep(5)


def simulate_tx(address, sender, receiver, amount):
    data = {
        "sender": sender,
        "receiver": receiver,
        "amount": amount
    }

    req = urllib.request.Request(url="http://" + address + "/transactions/new",
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
