import json
import random
import threading
import time
import urllib.request
from argparse import ArgumentParser
from builtins import str
from random import randint

from flask import jsonify, request, Flask

import db
from p2p.node import NodeManager, Node
from script import Script, get_address_from_ripemd160
from wallet import Wallet

node_list = []
expectedClientNum = 4
defaultPort = 30134
serverIP = "121.36.95.93"
serverAddress = "121.36.95.93:30134"

app = Flask(__name__)


@app.route('/hello', methods=['POST'])
def server_hello():
    values = request.get_json()
    required = ['node_id', 'port', 'wallet', 'pubkey_hash']
    if not all(k in values for k in required):
        return 'Missing values', 400
    values["ip"] = request.environ['REMOTE_ADDR']
    node_list.append(values)

    return 'hello', 200


def client_hello():
    output = {
        'node_id': node_manager.node_id,
        'port': node_manager.port,
        'wallet': blockchain.get_wallet_address(),
        'pubkey_hash': Script.sha160(str(blockchain.wallet.pubkey))
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
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    return res


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
        print(seed_list)
        bootstrap(str(node["ip"]) + ":" + str(node["port"]), seed_list)

    print()
    "ok"

    node_manager.start();

    time.sleep(1)

    node1_wallet = node_list[0]["wallet"]
    node2_wallet = node_list[1]["wallet"]
    node3_wallet = node_list[2]["wallet"]

    node1_address = str(node_list[0]["ip"]) + ":" + str(node_list[0]["port"])
    node2_address = str(node_list[1]["ip"]) + ":" + str(node_list[1]["port"])
    node3_address = str(node_list[2]["ip"]) + ":" + str(node_list[2]["port"])

    while True:
        # node1 发送给node2 node3
        node1_balance = get_balance(node1_address, node1_wallet)
        node1_balance = node1_balance['balance']
        if node1_balance > 0:
            amount = random.randint(1, node1_balance) / 10
            print('send from node1 to node2 with amount:' + str(amount))
            simulate_tx(node1_address, node1_wallet, node2_wallet, amount)
            time.sleep(random.randint(4, 5))

        node1_balance = get_balance(node1_address, node1_wallet)
        node1_balance = node1_balance['balance']
        if node1_balance > 0:
            amount = random.randint(1, node1_balance) / 10
            print('send from node1 to node3 with amount:' + str(amount))
            simulate_tx(node1_address, node1_wallet, node3_wallet, amount)
            time.sleep(random.randint(4, 5))

        # node2 发送给node1 node3
        node2_balance = get_balance(node2_address, node2_wallet)
        node2_balance = node2_balance['balance']
        if node2_balance > 0:
            amount = random.randint(1, node2_balance) / 10
            print('send from node2 to node1 with amount:' + str(amount))
            simulate_tx(node2_address, node2_wallet, node1_wallet, amount)
            time.sleep(random.randint(4, 5))

        node2_balance = get_balance(node2_address, node2_wallet)
        node2_balance = node2_balance['balance']
        if node2_balance > 0:
            amount = random.randint(1, node2_balance) / 10
            print('send from node2 to node3 with amount:' + str(amount))
            simulate_tx(node2_address, node2_wallet, node3_wallet, amount)
            time.sleep(random.randint(4, 5))
        #
        # node3 发送给node1 node2
        node3_balance = get_balance(node3_address, node3_wallet)
        node3_balance = node3_balance['balance']
        if node3_balance > 0:
            amount = random.randint(1, node3_balance) / 10
            print('send from node3 to node1 with amount:' + str(amount))
            simulate_tx(node3_address, node3_wallet, node1_wallet, amount)
            time.sleep(random.randint(4, 5))

        node3_balance = get_balance(node3_address, node3_wallet)
        node3_balance = node3_balance['balance']
        if node3_balance > 0:
            amount = random.randint(1, node3_balance) / 10
            print('send from node3 to node2 with amount:' + str(amount))
            simulate_tx(node3_address, node3_wallet, node2_wallet, amount)
            time.sleep(random.randint(4, 5))
        time.sleep(5)


def simulate_tx(address, sender, receiver, amount):
    data = dict(sender=sender, receiver=receiver, amount=amount)

    req = urllib.request.Request(url="http://" + address + "/transactions/new",
                                 headers={"Content-Type": "application/json"}, data=json.dumps(data).encode('utf-8'))
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    return res


def get_balance(address, wallet_address):
    req = urllib.request.Request(url="http://" + address + "/balance?address=" + wallet_address,
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

    if not node_manager.is_primary:
        node_manager.start();

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



# @app.route('/chain', methods=['GET'])
# def full_chain():
#     output = {
#         'length': db.get_block_height(blockchain.wallet.address),
#         'chain': blockchain.json_output(),
#     }
#     json_output = json.dumps(output, indent=4)
#     return json_output, 200


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


@app.route('/height', methods=['GET'])
def block_height_app():
    response = {
        'code': 0,
        'value': db.get_block_height(blockchain.wallet.address)
    }
    return json.dumps(response), 200


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


@app.route('/block_info', methods=['GET'])
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
        'difficulty': block.difficulty,
        'nonce': block.nonce,
        'transactions': json_transaction
    }

    return jsonify(response), 200


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-s', action='store_true')
    args = parser.parse_args()
    isServer = args.s

    if isServer:

        node_manager = NodeManager('0.0.0.0', defaultPort, isServer, True, expectedClientNum)
        blockchain = node_manager.blockchain

        print("Wallet address: %s" % blockchain.get_wallet_address())

        thread = threading.Thread(target=app.run, args=('0.0.0.0', defaultPort))
        thread.setDaemon(True)
        thread.start()

        time.sleep(1)

        serverNode = {
            'node_id': node_manager.node_id,
            'ip': serverIP,
            'port': defaultPort,
            'wallet': blockchain.get_wallet_address(),
            'pubkey_hash': Script.sha160(str(blockchain.wallet.pubkey))
        }
        node_list.append(serverNode)
        start_simulation()

    else:

        port = randint(30000, 31000)

        node_manager = NodeManager('0.0.0.0', port, isServer, True)
        blockchain = node_manager.blockchain

        print("Wallet address: %s" % blockchain.get_wallet_address())

        thread = threading.Thread(target=app.run, args=('0.0.0.0', port))
        thread.setDaemon(True)
        thread.start()

        time.sleep(1)
        client_hello()
        thread.join()