import asyncio
import json
import random
import threading
import time, os
import urllib.request
from argparse import ArgumentParser
from builtins import str
import random
from flask import jsonify, request, Flask
import configparser

import db
from p2p.node import NodeManager, Node
from script import Script, get_address_from_ripemd160
from wallet import Wallet
from transaction import Transaction, Tx_vid, Tx_report, Tx_easy

import sys
import traci

node_list = []
defaultPort = 30134
serverIP = "121.36.95.93" # "127.0.0.1"
serverAddress = "121.36.95.93:30134" # "127.0.0.1:30134"

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  

app = Flask(__name__)


@app.route('/hello', methods=['POST'])
def server_hello():
    values = request.get_json()
    required = ['node_id', 'port', 'wallet', 'pubkey_hash']
    if not all(k in values for k in required):
        return 'Missing values', 400
    values["ip"] = request.environ['REMOTE_ADDR']
    is_new_node=values['is_new_node']
    del(values['is_new_node'])
    node_list.append(values)
    if is_new_node:
        node=values
        seed_list = []
        for peer in node_list:
            if node != peer:
                seed_list.append({"node_id": peer["node_id"], "ip": peer["ip"], "port": peer["port"]})
        # print(seed_list)
        bootstrap(str(node["ip"]) + ":" + str(node["port"]), seed_list)
        time.sleep(5)
        node_manager.introduce_neighbour(node_list)
        

    return 'hello', 200


def client_hello(is_new_node):
    output = {
        'node_id': node_manager.node_id,
        'port': node_manager.port,
        'wallet': blockchain.get_wallet_address(),
        'pubkey_hash': Script.sha160(str(blockchain.wallet.pubkey)),
        'is_new_node': is_new_node
    }
    output = json.dumps(output, default=lambda obj: obj.__dict__, indent=4)

    req = urllib.request.Request("http://" + serverAddress + "/hello",
                                 output.encode("utf-8"),
                                 {"Content-Type": "application/json"})
    urllib.request.urlopen(req)


def bootstrap(address, seeds):
    data = {
        "seeds": seeds
    }
    req = urllib.request.Request("http://" + address + "/bootstrap",
                                 json.dumps(data).encode('utf-8'),
                                 {"Content-Type": "application/json"})

    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(e)


def request_seeds(wallet_address):
    cf = configparser.ConfigParser()
    cf.read(wallet_address + '/IoTBlockchain.conf')
    node_manager.primary_node_address = cf.get('meta', 'primary_node_address')
    node_manager.sendrestart()


# async def start_simulation():
def start_simulation():

    while True:
        if len(node_list) == expectedClientNum:
            break
        time.sleep(.1)

    for node in node_list:
        seed_list = []
        for peer in node_list:
            if node != peer:
                seed_list.append({"node_id": peer["node_id"], "ip": peer["ip"], "port": peer["port"]})
        # print(seed_list)
        bootstrap(str(node["ip"]) + ":" + str(node["port"]), seed_list)

    # print("ok")

    node_manager.start()

    time.sleep(1)

    sumo_tx()

    # first distribute some token to every nodes
    # for recv in range(1, len(node_list)):
    #     perform_transaction(0, recv)

    # while True:
    #     await asyncio.gather(*(generate_transactions(i) for i in range(0, len(node_list))))


def sumo_tx():
    for step in range(0,15000):
        traci.simulationStep()
        # print(traci.simulation.getDepartedIDList())
        if step >= 2:
            for vid in traci.simulation.getDepartedIDList():
                n = random.randint(0, len(node_list) - 1)
                addr = str(node_list[n]["ip"]) + ":" + str(node_list[n]["port"])
                print(f"[Tx] New Vehicle: {vid} registered in RSU {n}")
                vid_reg_tx(addr, vid)
            if step % 5 == 0:
                v1 = round(traci.edge.getLastStepMeanSpeed('m1'), 3)
                v2 = round(traci.edge.getLastStepMeanSpeed('m4'), 3)
                n1 = traci.edge.getLastStepVehicleNumber('m1')
                n2 = traci.edge.getLastStepVehicleNumber('m4')
                print("[Tx] Main Street Report:", end = " ")
                print(f'(m1, {v1}, {n1}), (m4, {v2}, {n2})')
                n = random.randint(0, len(node_list) - 1)
                addr = str(node_list[n]["ip"]) + ":" + str(node_list[n]["port"])
                main_street_tx(addr, 'm1', v1, n1)
                main_street_tx(addr, 'm4', v2, n2)
            time.sleep(.5)
    traci.close()    


# async def generate_transactions(sender):
#     await asyncio.sleep(random.expovariate(0.5))
#     receiver = random.randint(0, len(node_list)-1)
#     if receiver == sender:
#         receiver = (receiver + 1) % len(node_list)

#     perform_transaction(sender, receiver)


# def perform_transaction(sender, receiver, amount=-1):

#     sender_wallet = node_list[sender]["wallet"]
#     receiver_wallet = node_list[receiver]["wallet"]

#     sender_address = str(node_list[sender]["ip"]) + ":" + str(node_list[sender]["port"])

#     # if not amount > 0:
#     #     sender_balance = get_balance(sender_address, sender_wallet)

#     #     if sender_balance is None:
#     #         return

#     #     sender_balance = sender_balance['balance']

#     #     if sender_balance <= 0:
#     #         return

#     #     amount = random.random() * sender_balance / 10

#     amount = random.randint(1, 10)

#     print('[Tx] send from node ' + str(sender) + ' to node ' + str(receiver) + ' with amount:' + str(amount))
#     simulate_tx(sender_address, sender_wallet, receiver_wallet, amount)



def simulate_tx(address, sender, receiver, amount):
    data = dict(sender=sender, receiver=receiver, amount=amount)

    req = urllib.request.Request(url="http://" + address + "/transactions/new_easy",
                                 headers={"Content-Type": "application/json"}, data=json.dumps(data).encode('utf-8'))
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    return res


def vid_reg_tx(address, vid):
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



def get_balance(address, wallet_address):
    req = urllib.request.Request(url="http://" + address + "/balance?address=" + wallet_address,
                                 headers={"Content-Type": "application/json"})

    try:
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        return json.loads(res)
    except Exception as e:
        print(e)
        return None


def get_node_info(address):
    req = urllib.request.Request(url="http://" + address + "/curr_node",
                                 headers={"Content-Type": "application/json"})

    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    return json.loads(res)


@app.route('/bootstrap', methods=['POST'])
def bootstrap_app():
    values = request.get_json()
    required = ['seeds']
    if not all(k in values for k in required):
        return 'Missing values', 400
    seeds = values['seeds']
    # print json.dumps(seeds, default=lambda obj: obj.__dict__, indent=4)
    seed_nodes = list()
    for seed in seeds:
        seed_nodes.append(Node(seed['ip'], seed['port'], seed['node_id']))
    node_manager.bootstrap(seed_nodes)

    all_nodes = node_manager.buckets.get_all_nodes()
    output = json.dumps(all_nodes, default=lambda obj: obj.__dict__, indent=4)

    return output, 200


@app.route('/curr_node', methods=['GET'])
def curr_node_app():
    output = {
        'node_id': node_manager.node_id,
        'ip': node_manager.ip,
        'port': node_manager.port,
        'wallet': blockchain.get_wallet_address(),
        'pubkey_hash': Script.sha160(str(blockchain.wallet.pubkey))
    }
    output = json.dumps(output, default=lambda obj: obj.__dict__, indent=4)
    return output, 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction_app():
    values = request.get_json()
    required = ['sender', 'receiver', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    new_tx = blockchain.new_utxo_transaction(values['sender'], values['receiver'], values['amount'])

    if new_tx:
        # 广播交易
        node_manager.sendtx(new_tx)
        output = {
            'message': 'new transaction been created successfully!',
            'current_transactions': [tx.json_output() for tx in blockchain.current_transactions]
        }
        json_output = json.dumps(output, indent=4)
        return json_output, 200

    else:
        response = {'message': "Not enough funds!"}
        return jsonify(response), 200


@app.route('/transactions/new_easy', methods=['POST'])
def new_easy_transaction():
    values = request.get_json()
    required = ['sender', 'receiver', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    new_tx = blockchain.new_easy_transaction(values['sender'], values['receiver'], values['amount'])

    output = {
        'message': 'new transaction been created successfully!',
        'received_transactions': [tx.json_output() for tx in blockchain.received_transactions]
    }
    json_output = json.dumps(output, indent=4)
    return json_output, 200


@app.route('/transactions/new_vid', methods=['POST'])
def new_vid_transaction():
    values = request.get_json()
    required = ['vid']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    new_tx = blockchain.new_vid_transaction(values['vid'])

    output = {
        'message': 'new transaction been created successfully!',
        'received_transactions': [tx.json_output() for tx in blockchain.received_transactions]
    }
    json_output = json.dumps(output, indent=4)
    return json_output, 200


@app.route('/transactions/new_report', methods=['POST'])
def new_report_tx():
    values = request.get_json()
    required = ['edgeId', 'meanSpeed', 'vehicleNum']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    new_tx = blockchain.new_report_tx(values['edgeId'], values['meanSpeed'], values['vehicleNum'])

    output = {
        'message': 'new transaction been created successfully!',
        'received_transactions': [tx.json_output() for tx in blockchain.received_transactions]
    }
    json_output = json.dumps(output, indent=4)
    return json_output, 200


@app.route('/balance', methods=['GET'])
def get_balance_app():
    address = request.args.get('address')
    response = {
        'address': address,
        'balance': blockchain.get_balance_by_db(address)
    }
    return jsonify(response), 200


@app.route('/node_info', methods=['POST'])
def node_info_app():
    values = request.get_json()
    required = ['ip', 'port']
    if not all(k in values for k in required):
        return 'Missing values', 400

    ip = values['ip']
    port = values['port']
    block_height = db.get_block_height(blockchain.wallet.address)
    latest_block = db.get_block_data_by_index(blockchain.wallet.address, block_height - 1)
    block_hash = latest_block.current_hash
    timestamp = latest_block.timestamp

    time_local = time.localtime(timestamp)

    response = {
        'address': ip + ':' + str(port),
        'block_height': block_height,
        'block_hash': block_hash,
        'wallet_address': blockchain.wallet.address,
        # 'balance': blockchain.get_balance(blockchain.wallet.address),
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    }
    return jsonify(response), 200


@app.route('/tx_info', methods=['GET'])
def tx_info_app():

    block_index = int(request.args.get('block_index'))
    txid = request.args.get('txid')

    block = db.get_block_data_by_index(blockchain.wallet.address, block_index)
    for tx in block.transactions:
        if tx.txid == txid:
            return json.dumps(tx.json_output()), 200

    return 'not exist!', 200


@app.route('/unconfirm_tx_info', methods=['GET'])
def unconfirm_tx_info_app():
    txid = request.args.get('txid')

    for tx in db.get_all_unconfirmed_tx(blockchain.wallet.address):
        if tx.txid == txid:
            return json.dumps(tx.json_output()), 200

    return 'not exist!', 200


@app.route('/tx_in_block', methods=['GET'])
def tx_in_block():
    values = request.get_json()

    block_index = int(request.args.get('block_index'))

    block = db.get_block_data_by_index(blockchain.wallet.address, block_index)
    tmp = dict()
    cnt = 0
    for tx in block.transactions:
        if isinstance(tx, Tx_vid):
            tmp[str(cnt)] = {
                'txid': tx.txid,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(tx.timestamp)),
                'type': 'vid',
                'vid': tx.vid
            }
            cnt += 1
        
        elif isinstance(tx, Tx_report):
            tmp[str(cnt)] = {
                'txid': tx.txid,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(tx.timestamp)),
                'type': 'report',
                'edgeId': tx.edgeId,
                'meanSpeed': tx.meanSpeed,
                'vehicleNum': tx.vehicleNum
            }
            cnt += 1
        
        elif isinstance(tx, Tx_easy):
            tmp[str(cnt)] = {
                'txid': tx.txid,
                'sender': tx.sender,
                'receiver': tx.receiver,
                'amount': tx.amount,
                'timestamp': tx.timestamp
            }
            cnt += 1

        elif isinstance(tx, Transaction):
            txins = tx.txins
            txouts = tx.txouts
            
            from_addr = list()
            to_addr = list()
            amount = 0

            for txin in txins:
                if txin.prev_tx_out_idx != -1:
                    address = Wallet.get_address(txin.pubkey)
                    if address not in from_addr:
                        from_addr.append(address)
            
            for txout in txouts:
                value = txout.value
                script_pub_key = txout.scriptPubKey
                if len(script_pub_key) == 5:
                    recv_addr = get_address_from_ripemd160(script_pub_key[2])
                    to_addr.append({'receiver': recv_addr, 'value': value})
            
            tmp[str(cnt)] = {
                'txid': tx.txid,
                'senders': from_addr,
                'receivers': to_addr,
                'amount': amount,
                'timestamp': tx.timestamp
            }

            cnt += 1
            
    return json.dumps(tmp), 200


@app.route('/block_time', methods=['GET'])
def block_time():
    output = node_manager.blocktime
    output = json.dumps(output, default=lambda obj: obj.__dict__, indent=4)
    return output, 200


@app.route('/get_block_time', methods=['GET'])
def get_block_time():
    view = request.args.get('view')
    view = int(view)
    if view in node_manager.blocktime.keys():
        response = {
            'view': view,
            'time': node_manager.blocktime[view]
        }
        return jsonify(response), 200
    else:
        return "Missing value", 200


@app.route('/height', methods=['GET'])
def block_height_app():
    response = {
        'code': 0,
        'value': db.get_block_height(blockchain.wallet.address)
    }
    return json.dumps(response), 200


@app.route('/GST', methods=['GET'])
def getGST():
    response = {
        'GST': node_manager.GST
    }
    return json.dumps(response), 200


@app.route('/step', methods=['GET'])
def get_step():
    response = {
        'step': node_manager.step
    }
    return json.dumps(response), 200


@app.route('/asyn_node', methods=['GET'])
def asyn_node():
    view = request.args.get('view')

    rate = round(node_manager.asyn[int(view)] / (node_manager.numSeedNode + 1), 3)

    response = {
        'view': int(view),
        'numAsyn': node_manager.asyn[int(view)],
        'numSeedNode': node_manager.numSeedNode,
        'rate': rate
    }

    return jsonify(response), 200


@app.route('/asyn_node_all', methods=['GET'])
def asyn_node_all():
    response = {
        'numAsyn': node_manager.asyn,
        'numSeedNode': node_manager.numSeedNode,
    }

    return jsonify(response), 200


@app.route('/consensus_time', methods=['GET'])
def consensus_time():
    view = request.args.get('view')

    response = {
        'view': int(view),
        'time': node_manager.consensus[int(view)]
    }

    return jsonify(response), 200


@app.route('/consensus_time_all', methods=['GET'])
def consensus_time_all():
    return jsonify(node_manager.consensus), 200


@app.route('/latest_tx', methods=['GET'])
def latest_tx_app():
    json_transaction = list()
    for tx in db.get_all_unconfirmed_tx(blockchain.wallet.address):
        txins = tx.txins
        txouts = tx.txouts

        from_addr = list()
        to_addr = list()
        amount = 0
        for txin in txins:
            if txin.prev_tx_out_idx != -1:
                pubkey_hash = Wallet.get_address(txin.pubkey)
                if pubkey_hash not in from_addr:
                    from_addr.append(pubkey_hash)

        for txout in txouts:
            value = txout.value
            script_pub_key = txout.scriptPubKey
            if len(script_pub_key) == 5:
                recv_addr = get_address_from_ripemd160(script_pub_key[2])
                to_addr.append({'receiver': recv_addr, 'value': value})

        new_tx = {
            'txid': tx.txid,
            'senders': from_addr,
            'receivers': to_addr,
            'amount': amount,
            'timestamp': tx.timestamp
        }

        json_transaction.append(new_tx)

    response = {
        'latest_tx': json_transaction
    }
    return json.dumps(response), 200


@app.route('/block_info_tx', methods=['GET'])
def block_info_app():
    height = request.args.get('height')
    block_index = int(height) - 1

    block = db.get_block_data_by_index(blockchain.wallet.address, block_index)

    json_transaction = list()
    for tx in block.transactions:
        txins = tx.txins
        txouts = tx.txouts

        from_addr = list()
        to_addr = list()
        amount = 0
        for txin in txins:
            if txin.prev_tx_out_idx != -1:
                address = Wallet.get_address(txin.pubkey)
                if address not in from_addr:
                    from_addr.append(address)

        for txout in txouts:
            value = txout.value
            script_pub_key = txout.scriptPubKey
            if len(script_pub_key) == 5:
                recv_addr = get_address_from_ripemd160(script_pub_key[2])
                to_addr.append({'receiver': recv_addr, 'value': value})

        new_tx = {
            'txid': tx.txid,
            'senders': from_addr,
            'receivers': to_addr,
            'amount': amount,
            'timestamp': tx.timestamp
        }

        json_transaction.append(new_tx)

    response = {
        'index': block.index,
        'current_hash': block.current_hash,
        'previous_hash': block.previous_hash,
        'timestamp': block.timestamp,
        'merkleroot': block.merkleroot,
        'nonce': block.nonce,
        'transactions': json_transaction
    }

    return jsonify(response), 200


@app.route('/block_info', methods=['GET'])
def block_info():
    block_index = request.args.get('block_index')

    block = db.get_block_data_by_index(blockchain.wallet.address, block_index)

    json_transaction = list()
    for tx in block.transactions:
        if isinstance(tx, Tx_vid):
            new_tx = {
                'txid': tx.txid,
                'timestamp': tx.timestamp,
                'type': 'vid',
                'vid': tx.vid
            }
        elif isinstance(tx, Tx_report):
            new_tx = {
                'txid': tx.txid,
                'timestamp': tx.timestamp,
                'type': 'report',
                'edgeId': tx.edgeId,
                'meanSpeed': tx.meanSpeed,
                'vehicleNum': tx.vehicleNum
            }
        elif isinstance(tx, Tx_easy):
            new_tx = {
                'txid': tx.txid,
                'sender': tx.sender,
                'receiver': tx.receiver,
                'amount': tx.amount,
                'timestamp': tx.timestamp
            }
        elif isinstance(tx, Transaction):
            txins = tx.txins
            txouts = tx.txouts
            
            from_addr = list()
            to_addr = list()
            amount = 0

            for txin in txins:
                if txin.prev_tx_out_idx != -1:
                    address = Wallet.get_address(txin.pubkey)
                    if address not in from_addr:
                        from_addr.append(address)
            
            for txout in txouts:
                value = txout.value
                script_pub_key = txout.scriptPubKey
                if len(script_pub_key) == 5:
                    recv_addr = get_address_from_ripemd160(script_pub_key[2])
                    to_addr.append({'receiver': recv_addr, 'value': value})
            
            new_tx = {
                'txid': tx.txid,
                'senders': from_addr,
                'receivers': to_addr,
                'amount': amount,
                'timestamp': tx.timestamp
            }

        json_transaction.append(new_tx)

    response = {
        'index': block.index,
        'timestamp': block.timestamp,
        'current_hash': block.current_hash,
        'previous_hash': block.previous_hash,
        'merkleroot': block.merkleroot,
        'transactions': json_transaction
    }

    return jsonify(response), 200

def print_hello():
    print('''
    ███████╗ ██████╗       ██╗   ██╗███╗   ██╗
    ██╔════╝██╔════╝       ██║   ██║████╗  ██║
    ███████╗██║  ███╗█████╗██║   ██║██╔██╗ ██║
    ╚════██║██║   ██║╚════╝╚██╗ ██╔╝██║╚██╗██║
    ███████║╚██████╔╝       ╚████╔╝ ██║ ╚████║
    ╚══════╝ ╚═════╝         ╚═══╝  ╚═╝  ╚═══╝                                   
    ''')

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-s', action='store_true', help='server node')
    parser.add_argument('-n', default=4, type=int, help='number of expected nodes')
    parser.add_argument('-p', '--port', default=defaultPort, type=int, help='port to listen on, must be used together with -r')
    parser.add_argument('-r', action='store_true', help='restart, must be used together with -p')
    parser.add_argument('-c',action='store_true', help='new node')
    parser.add_argument("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    args = parser.parse_args()
    isServer = args.s
    expectedClientNum = args.n
    re = args.r
    try:
        argPort = args.p
    except AttributeError:
        print('~')
    is_new_node = args.c
    if args.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    if isServer:
        traci.start([sumoBinary, "-c", "simulation.sumocfg"])
        
        node_manager = NodeManager('0.0.0.0', [(serverIP, defaultPort)], defaultPort, isServer, True, False, expectedClientNum, isServer)
        # node_manager = NodeManager('127.0.0.1', [(serverIP, defaultPort)], defaultPort, isServer, True, False, expectedClientNum, isServer)
        blockchain = node_manager.blockchain

        print("[Info] Wallet Address: %s" % blockchain.get_wallet_address())

        thread = threading.Thread(target=app.run, args=('0.0.0.0', defaultPort))
        thread.setDaemon(True)
        thread.start()

        serverNode = {
            'node_id': node_manager.node_id,
            'ip': serverIP,
            'port': defaultPort,
            'wallet': blockchain.get_wallet_address(),
            'pubkey_hash': Script.sha160(str(blockchain.wallet.pubkey))
        }
        node_list.append(serverNode)
        print_hello()
        loop =asyncio.get_event_loop()
        loop.run_until_complete(start_simulation())

        thread.join()

    else:

        if re:
            lport = argPort
        else:
            lport = random.randint(30000, 31000)

        node_manager = NodeManager('0.0.0.0', [(serverIP, defaultPort)], lport, isServer, True, False, expectedClientNum, isServer)
        # node_manager = NodeManager('127.0.0.1', [(serverIP, defaultPort)], lport, isServer, True, False, expectedClientNum, isServer)
        blockchain = node_manager.blockchain

        print("[Info] Wallet Address: %s" % blockchain.get_wallet_address())

        thread = threading.Thread(target=app.run, args=('0.0.0.0', lport))
        thread.setDaemon(True)
        thread.start()

        # shall be await app started
        time.sleep(5)
        if re:
            print('-------Restart-------')
            request_seeds(blockchain.get_wallet_address())
        print_hello()
        client_hello(is_new_node)

        thread.join()
