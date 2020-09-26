# coding:utf-8
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import json
import random
import time
import urllib.request, urllib.error, urllib.parse


def bootstrap(address, seeds):
    data = {
        "seeds": seeds
    }
    req = urllib.request.Request("http://" + address + "/bootstrap",
                          json.dumps(data),
                          {"Content-Type": "application/json"})
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    return res

def run():
    node1 = get_node_info("127.0.0.1:5000")
    node2 = get_node_info("127.0.0.1:5001")
    node3 = get_node_info("127.0.0.1:5002")
    node4 = get_node_info("127.0.0.1:5003")
    node5 = get_node_info("127.0.0.1:5004")
    node6 = get_node_info("127.0.0.1:5005")
    node7 = get_node_info("127.0.0.1:5006")
    node8 = get_node_info("127.0.0.1:5007")
    node9 = get_node_info("127.0.0.1:5008")
    node10 = get_node_info("127.0.0.1:5009")
 

    node1_seeds = [
	
        {"node_id": node2["node_id"], "ip":node2["ip"], "port":node2["port"]},
        {"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]},
	#{"node_id": node4["node_id"], "ip": node4["ip"], "port": node4["port"]},
	#{"node_id": node5["node_id"], "ip": node5["ip"], "port": node5["port"]},
	{"node_id": node6["node_id"], "ip": node6["ip"], "port": node6["port"]},
	{"node_id": node7["node_id"], "ip": node7["ip"], "port": node7["port"]},
	{"node_id": node8["node_id"], "ip": node8["ip"], "port": node8["port"]},
	{"node_id": node9["node_id"], "ip": node9["ip"], "port": node9["port"]},
	{"node_id": node10["node_id"], "ip": node10["ip"], "port": node10["port"]}
	
    ]
    i1=bootstrap("127.0.0.1:5000", node1_seeds)
    print(i1)
    node2_seeds = [
        {"node_id": node1["node_id"], "ip":node1["ip"], "port":node1["port"]},
       
        #{"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]},
	{"node_id": node4["node_id"], "ip": node4["ip"], "port": node4["port"]},
	{"node_id": node5["node_id"], "ip": node5["ip"], "port": node5["port"]},
	{"node_id": node6["node_id"], "ip": node6["ip"], "port": node6["port"]},
	{"node_id": node7["node_id"], "ip": node7["ip"], "port": node7["port"]},
	{"node_id": node8["node_id"], "ip": node8["ip"], "port": node8["port"]},
	#{"node_id": node9["node_id"], "ip": node9["ip"], "port": node9["port"]},
	{"node_id": node10["node_id"], "ip": node10["ip"], "port": node10["port"]}
	]
    i2=bootstrap("127.0.0.1:5001", node2_seeds)
    print(i2)
    node3_seeds = [
        {"node_id": node1["node_id"], "ip":node1["ip"], "port":node1["port"]},
        #{"node_id": node2["node_id"], "ip":node2["ip"], "port":node2["port"]},
        
	{"node_id": node4["node_id"], "ip": node4["ip"], "port": node4["port"]},
	{"node_id": node5["node_id"], "ip": node5["ip"], "port": node5["port"]},
	#{"node_id": node6["node_id"], "ip": node6["ip"], "port": node6["port"]},
	{"node_id": node7["node_id"], "ip": node7["ip"], "port": node7["port"]},
	#{"node_id": node8["node_id"], "ip": node8["ip"], "port": node8["port"]},
	{"node_id": node9["node_id"], "ip": node9["ip"], "port": node9["port"]},
	{"node_id": node10["node_id"], "ip": node10["ip"], "port": node10["port"]}
    ]
    i3=bootstrap("127.0.0.1:5002", node3_seeds)
    print(i3)
    node4_seeds=[
	#{"node_id": node1["node_id"], "ip":node1["ip"], "port":node1["port"]},
        {"node_id": node2["node_id"], "ip":node2["ip"], "port":node2["port"]},
        {"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]},
	
	#{"node_id": node5["node_id"], "ip": node5["ip"], "port": node5["port"]},
	#{"node_id": node6["node_id"], "ip": node6["ip"], "port": node6["port"]},
	{"node_id": node7["node_id"], "ip": node7["ip"], "port": node7["port"]},
	{"node_id": node8["node_id"], "ip": node8["ip"], "port": node8["port"]},
	{"node_id": node9["node_id"], "ip": node9["ip"], "port": node9["port"]},
	{"node_id": node10["node_id"], "ip": node10["ip"], "port": node10["port"]}
	]
    node5_seeds=[
	#{"node_id": node1["node_id"], "ip":node1["ip"], "port":node1["port"]},
        {"node_id": node2["node_id"], "ip":node2["ip"], "port":node2["port"]},
        {"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]},
	#{"node_id": node4["node_id"], "ip": node4["ip"], "port": node4["port"]},
	
	{"node_id": node6["node_id"], "ip": node6["ip"], "port": node6["port"]},
	{"node_id": node7["node_id"], "ip": node7["ip"], "port": node7["port"]},
	{"node_id": node8["node_id"], "ip": node8["ip"], "port": node8["port"]},
	{"node_id": node9["node_id"], "ip": node9["ip"], "port": node9["port"]},
	{"node_id": node10["node_id"], "ip": node10["ip"], "port": node10["port"]}
	]
    node6_seeds=[
	{"node_id": node1["node_id"], "ip":node1["ip"], "port":node1["port"]},
        {"node_id": node2["node_id"], "ip":node2["ip"], "port":node2["port"]},
        #{"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]},
	#{"node_id": node4["node_id"], "ip": node4["ip"], "port": node4["port"]},
	{"node_id": node5["node_id"], "ip": node5["ip"], "port": node5["port"]},
	
	{"node_id": node7["node_id"], "ip": node7["ip"], "port": node7["port"]},
	#{"node_id": node8["node_id"], "ip": node8["ip"], "port": node8["port"]},
	{"node_id": node9["node_id"], "ip": node9["ip"], "port": node9["port"]},
	{"node_id": node10["node_id"], "ip": node10["ip"], "port": node10["port"]}
	]
    node7_seeds=[
	{"node_id": node1["node_id"], "ip":node1["ip"], "port":node1["port"]},
        {"node_id": node2["node_id"], "ip":node2["ip"], "port":node2["port"]},
        {"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]},
	{"node_id": node4["node_id"], "ip": node4["ip"], "port": node4["port"]},
	{"node_id": node5["node_id"], "ip": node5["ip"], "port": node5["port"]},
	{"node_id": node6["node_id"], "ip": node6["ip"], "port": node6["port"]},
	
	#{"node_id": node8["node_id"], "ip": node8["ip"], "port": node8["port"]},
	#{"node_id": node9["node_id"], "ip": node9["ip"], "port": node9["port"]},
	{"node_id": node10["node_id"], "ip": node10["ip"], "port": node10["port"]}
	]
    node8_seeds=[
	{"node_id": node1["node_id"], "ip":node1["ip"], "port":node1["port"]},
        {"node_id": node2["node_id"], "ip":node2["ip"], "port":node2["port"]},
        #{"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]},
	{"node_id": node4["node_id"], "ip": node4["ip"], "port": node4["port"]},
	{"node_id": node5["node_id"], "ip": node5["ip"], "port": node5["port"]},
	#{"node_id": node6["node_id"], "ip": node6["ip"], "port": node6["port"]},
	#{"node_id": node7["node_id"], "ip": node7["ip"], "port": node7["port"]},
	
	{"node_id": node9["node_id"], "ip": node9["ip"], "port": node9["port"]},
	{"node_id": node10["node_id"], "ip": node10["ip"], "port": node10["port"]}
	]
    node9_seeds=[
	{"node_id": node1["node_id"], "ip":node1["ip"], "port":node1["port"]},
        #{"node_id": node2["node_id"], "ip":node2["ip"], "port":node2["port"]},
        {"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]},
	{"node_id": node4["node_id"], "ip": node4["ip"], "port": node4["port"]},
	{"node_id": node5["node_id"], "ip": node5["ip"], "port": node5["port"]},
	{"node_id": node6["node_id"], "ip": node6["ip"], "port": node6["port"]},
	#{"node_id": node7["node_id"], "ip": node7["ip"], "port": node7["port"]},
	{"node_id": node8["node_id"], "ip": node8["ip"], "port": node8["port"]},
	
	{"node_id": node10["node_id"], "ip": node10["ip"], "port": node10["port"]}
	]
    node10_seeds=[
	{"node_id": node1["node_id"], "ip":node1["ip"], "port":node1["port"]},
        {"node_id": node2["node_id"], "ip":node2["ip"], "port":node2["port"]},
        {"node_id": node3["node_id"], "ip": node3["ip"], "port": node3["port"]},
	{"node_id": node4["node_id"], "ip": node4["ip"], "port": node4["port"]},
	{"node_id": node5["node_id"], "ip": node5["ip"], "port": node5["port"]},
	{"node_id": node6["node_id"], "ip": node6["ip"], "port": node6["port"]},
	{"node_id": node7["node_id"], "ip": node7["ip"], "port": node7["port"]},
	{"node_id": node8["node_id"], "ip": node8["ip"], "port": node8["port"]},
	{"node_id": node9["node_id"], "ip": node9["ip"], "port": node9["port"]},
	]
    bootstrap("127.0.0.1:5004", node5_seeds)
    bootstrap("127.0.0.1:5005", node6_seeds)
    bootstrap("127.0.0.1:5006", node7_seeds)
    bootstrap("127.0.0.1:5007", node8_seeds)
    bootstrap("127.0.0.1:5008", node9_seeds)
    bootstrap("127.0.0.1:5009", node10_seeds)
    bootstrap("127.0.0.1:5003", node4_seeds)
    time.sleep(1)

    node1_wallet = node1["wallet"]
    node2_wallet = node2["wallet"]
    node3_wallet = node3["wallet"]
    time.sleep(1)
    print("change")
    simubroad("127.0.0.1:5000","a test")
    print("end")
    


def simulate_tx(address, sender, receiver, amount):  
    data = {
        "sender": sender,
        "receiver": receiver,
        "amount": amount
    }

    req = urllib.request.Request(url="http://" + address + "/transactions/new",
                          headers={"Content-Type": "application/json"}, data=json.dumps(data))
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    return res


def get_balance(address, wallet_addres):
    req = urllib.request.Request(url="http://" + address + "/balance?address=" + wallet_addres,
                          headers={"Content-Type": "application/json"})

    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    return json.loads(res)


def get_node_info(address):
    req = urllib.request.Request(url="http://" + address + "/curr_node",
                          headers={"Content-Type": "application/json"})

    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    return json.loads(res)

def get_test_info(address):
    req=urllib.request.Request(url="http://" + address + "/test",
			  headers={"Content-Type": "application/json"})
    res_data=urllib.request.urlopen(req)
    res = res_data.read()
    return json.loads(res)

def lspr(address):#address对它lspr里的节点发送lspr需求
    req=urllib.request.Request(url="http://"+address+"/lspr",
                        headers={"Content-Type": "application/json"})
    res_data=urllib.request.urlopen(req)
    res = res_data.read()
    return json.loads(res)

def simubroad(address,message):
    data = {
        "message":message
        
    }

    req = urllib.request.Request(url="http://" + address + "/simubroad",
                          headers={"Content-Type": "application/json"},     	                  data=json.dumps(data))
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    return res,210
    
    



run()
