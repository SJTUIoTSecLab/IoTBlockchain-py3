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


def main_street_tx(address, edgeId, meanSpeed, num):
    data = {
        'edgeId': edgeId,
        'meanSpeed': meanSpeed,
        'vehicleNum': num
    }

    req = urllib.request.Request(url="http://" + address + "/transactions/new_report",
                          headers={"Content-Type": "application/json"}, data=bytes(json.dumps(data),'utf8'))
    res_data = urllib.request.urlopen(req)
    res = res_data.read().decode('utf8')
    return res


def prepare_nodes():
    node = list()
    for i in range(10):
        node.append(get_node_info("127.0.0.1:500" + str(i)))
        print('node', i+1)
    seeds = [
        {"node_id": node[i]["node_id"], "ip": node[i]["ip"], "port": node[i]["port"]} for i in range(10)
    ]
    for i in range(10):
        tmp = seeds[0]
        del seeds[0]
        bootstrap("127.0.0.1:500"+str(i), seeds)
        seeds.append(tmp)
    print("ok")
    time.sleep(1)


if __name__ == "__main__":
    options = get_options()   
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
    traci.start([sumoBinary, "-c", "simulation10.sumocfg"])

    for step in range(0,15000):
        traci.simulationStep()
        print(traci.simulation.getDepartedIDList())
        if step == 2:
            prepare_nodes()
        if step >= 2:
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
            if step % 2 == 0:
                v1 = round(traci.edge.getLastStepMeanSpeed('m1'), 3)
                v2 = round(traci.edge.getLastStepMeanSpeed('m4'), 3)
                n1 = traci.edge.getLastStepVehicleNumber('m1')
                n2 = traci.edge.getLastStepVehicleNumber('m4')
                print("main street report :")
                print('m1', v1, n1)
                print('m4', v2, n2)
                main_street_tx('127.0.0.1:5000', 'm1', v1, n1)
                main_street_tx('127.0.0.1:5001', 'm4', v2, n2)
            time.sleep(1)
    traci.close()
