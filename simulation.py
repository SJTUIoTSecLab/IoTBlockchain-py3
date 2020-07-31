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


import os
import sys
import optparse
import traci


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


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


def get_node_info(address):
    req = urllib.request.Request(url="http://" + address + "/curr_node",
                          headers={"Content-Type": "application/json"})

    res_data = urllib.request.urlopen(req)
    res = res_data.read().decode('utf8')
    return json.loads(res)


def simulate_tx(address, vid):
    data = {
        'vid': vid
    }

    req = urllib.request.Request(url="http://" + address + "/transactions/new_vid",
                          headers={"Content-Type": "application/json"}, data=bytes(json.dumps(data),'utf8'))
    res_data = urllib.request.urlopen(req)
    res = res_data.read().decode('utf8')
    return res


def prepare_nodes():
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


if __name__ == "__main__":
    options = get_options()   
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
    traci.start([sumoBinary, "-c", "simulation.sumocfg"])

    for step in range(0,15000):
        # traci.vehicle.setSpeed('a1.5',10)
        # print(traci.vehicle.getIDList())
        # print(traci.edge.getIDList())
        # print(traci.inductionloop.getVehicleData('abcd'))
        traci.simulationStep()
        print(traci.simulation.getDepartedIDList())
        if step == 3:
            prepare_nodes()
        if step >= 3:
            for vid in traci.simulation.getDepartedIDList():
                if vid.startswith('a'):
                    print("new vehicle:", vid)
                    print("signed in rsu 1")
                    simulate_tx("127.0.0.1:5000", vid)
                elif vid.startswith('b'):
                    print("new vehicle:", vid)
                    print("signed in rsu 2")
                    simulate_tx("127.0.0.1:5001", vid)
                elif vid.startswith('c'):
                    print("new vehicle:", vid)
                    print("signed in rsu 3")
                    simulate_tx("127.0.0.1:5002", vid) 
            time.sleep(1)
    traci.close()
