# coding:utf-8
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
from past.utils import old_div
import hashlib
import json
import socketserver
import pickle
import threading
import random

from Block import Block

import time
from binascii import Error

import zlib

import db
from blockchain import Blockchain
from p2p import constant
from p2p.kbucketset import KBucketSet
from p2p.nearestnodes import KNearestNodesUtil
from p2p import packet
from p2p.packet import Version, Verack

from copy import deepcopy


class ProcessMessages(socketserver.BaseRequestHandler):
    """
    服务端消息处理中心
    """

    def handle(self):
        """
        覆盖实现SocketServer.BaseRequestHandler类的handle方法
        专门接收处理来自服务端的请求

        备注：self.client_address是BaseRequestHandler的成员变量，记录连接到服务端的client地址
        :return:
        """
        msg_obj = pickle.loads(zlib.decompress(self.request[0]))

        command = msg_obj.payloadcommand = msg_obj.command
        payload = msg_obj.payloadcommand = msg_obj.payload
        

        # print 'Handle ', command, 'from ', self.client_address
        # print command, 'payload:', payload

        if command == "ping":
            self.handle_ping(payload)
        elif command == "pong":
            self.handle_pong(payload)
        elif command == "find_neighbors":
            self.handle_find_neighbors(payload)
        elif command == "found_neighbors":
            self.handle_found_neighbors(payload)
        elif command == "find_value":
            self.handle_find_value(payload)
        elif command == "found_value":
            self.handle_found_value(payload)
        elif command == "store":
            self.handle_store(payload)
        elif command == "sendrequestmessage":
            self.handle_sendrequestmessage(payload)
        elif command == "sendrequest":
            self.handle_sendrequest(payload)
        elif command == "sendtx":
            self.handle_sendtx(payload)
        elif command == "sendalltx":
            self.handle_sendalltx(payload)
        elif command == "sendblockhash":
            self.handle_sendblockhash(payload)
        elif command == "sendreply":
            self.handle_sendreply(payload)
        elif command == "sendblock":
            self.handle_sendblock(payload)
        elif command == "sendcorrect":
            self.handle_sendcorrect(payload)
        elif command == "sendfailhash":
            self.handle_sendfailhash(payload)
        elif command == "sendoff":
            self.handle_sendoff(payload)
        elif command == "version":
            self.handle_version(payload)
        elif command == "verack":
            self.handle_verack(payload)

            # client_node_id = payload.from_id
            # if self.server.node_manager.buckets.exist(client_node_id):
            #     self.server.node_manager.alive_nodes[client_node_id] = int(time.time())  # 更新节点联系时间

    def handle_ping(self, payload):
        socket = self.request[1]
        client_ip, client_port = self.client_address
        client_node_id = payload.from_id

        self.server.node_manager.pong(socket, client_node_id, (client_ip, client_port))

    def handle_pong(self, payload):
        pass

    def handle_find_neighbors(self, payload):
        socket = self.request[1]
        client_ip, client_port = self.client_address
        client_node_id = payload.from_id

        node_id = payload.target_id
        rpc_id = payload.rpc_id
        nearest_nodes = self.server.node_manager.buckets.nearest_nodes(node_id)
        if not nearest_nodes:
            nearest_nodes.append(self.server.node_manager.client)
        nearest_nodes_triple = [node.triple() for node in nearest_nodes]
        self.server.node_manager.found_neighbors(node_id, rpc_id, nearest_nodes_triple, socket, client_node_id,
                                                 (client_ip, client_port))

    def handle_found_neighbors(self, payload):
        rpc_id = payload.rpc_id
        k_nearest_nodes_util = self.server.node_manager.rpc_ids[rpc_id]
        del self.server.node_manager.rpc_ids[rpc_id]
        nearest_nodes = [Node(*node) for node in payload.neighbors]
        k_nearest_nodes_util.update(nearest_nodes)

    def handle_find_value(self, payload):
        socket = self.request[1]
        client_ip, client_port = self.client_address
        client_node_id = payload.from_id

        key = payload.key
        rpc_id = payload.rpc_id
        if str(key) in self.server.node_manager.data:
            value = self.server.node_manager.data[str(key)]
            self.server.node_manager.found_value(key, value, rpc_id, socket, client_node_id, (client_ip, client_port))
        else:
            nearest_nodes = self.server.node_manager.buckets.nearest_nodes(key)
            if not nearest_nodes:
                nearest_nodes.append(self.server.node_manager.client)
            nearest_nodes_triple = [node.triple() for node in nearest_nodes]
            self.server.node_manager.found_neighbors(key, rpc_id, nearest_nodes_triple, socket, client_node_id,
                                                     (client_ip, client_port))

    def handle_found_value(self, payload):
        rpc_id = payload.rpc_id
        value = payload.value
        k_nearest_nodes_util = self.server.node_manager.rpc_ids[rpc_id]
        del self.server.node_manager.rpc_ids[rpc_id]
        k_nearest_nodes_util.set_target_value(value)

    def handle_store(self, payload):
        key = payload.key
        value = payload.value
        self.server.node_manager.data[str(key)] = value

    def handle_sendtx(self, payload):
        # new_tx = payload
        # with self.server.node_manager.lock:
        #     blockchain = self.server.node_manager.blockchain
        #     # self.server.node_manager.receivetx = self.server.node_manager.receivetx + 1

        #     # 判断区块中是否存在
        #     if blockchain.find_transaction(new_tx.txid):
        #         return
        #     # 判断交易池中是否存在
        #     for k in range(len(blockchain.current_transactions)):
        #         uncomfirmed_tx = blockchain.current_transactions[-1 - k]
        #         if uncomfirmed_tx.txid == new_tx.txid:
        #             return

        #     blockchain.current_transactions.append(new_tx)
        #     blockchain.received_transactions.append(new_tx)
        #     db.write_unconfirmed_tx_to_db(blockchain.wallet.address, new_tx)
        pass

    def handle_sendalltx(self, payload):
        print("------handle alltx------")
        all_tx = payload["alltx"]
        tm = payload["time"]
        # GST = 10
        # self.server.node_manager.startflag = True
        # with self.server.node_manager.lock:
        if (tm + self.server.node_manager.GST > self.server.node_manager.maxTime):
            self.server.node_manager.maxTime = tm + self.server.node_manager.GST
        self.server.node_manager.receivealltx += 1

        with self.server.node_manager.lock:
            for new_tx in all_tx:
                # # 判断区块中是否存在
                # if blockchain.find_transaction(new_tx.txid):
                #     continue
                # # 判断交易池中是否存在
                # flag = True
                # for k in range(len(blockchain.current_transactions)):
                #     uncomfirmed_tx = blockchain.current_transactions[-1 - k]
                #     if uncomfirmed_tx.txid == new_tx.txid:
                #         flag = False
                #         break
                # if flag:
                self.server.node_manager.blockchain.current_transactions.append(new_tx)
            print("+++++an alltx added,the transaction now:+++++")            
            print("send tx:", len(self.server.node_manager.blockchain.send_transactions))
            print("received tx:", len(self.server.node_manager.blockchain.received_transactions))
            print("current tx:", len(self.server.node_manager.blockchain.current_transactions))

    def handle_sendblockhash(self, payload):
        print("------handle blockhash: the start of reply------")
        # with self.server.node_manager.lock:
        if payload['view'] == self.server.node_manager.view:
            self.server.node_manager.commitMessages.append(payload['blockhash'])
        print("+++++commitMessage now:+++++")
        print(self.server.node_manager.commitMessages)
        if not self.server.node_manager.finishflag:
            for b in self.server.node_manager.commitMessages:
                count = 0
                for b1 in self.server.node_manager.commitMessages:
                    if (b == b1):
                        count += 1
                if (count > old_div(self.server.node_manager.numSeedNode, 2)):
                    # db.write_to_db(blockchain.wallet.address, new_block)
                    print("-------------------I am correct!!!!!!!!--------------------")
                    self.server.node_manager.finishflag = True
                    self.server.node_manager.hashcache = b
                    self.server.node_manager.asyn[self.server.node_manager.view] = self.server.node_manager.numSeedNode - \
                      self.server.node_manager.commitMessages.count(self.server.node_manager.hashcache)
                    if not self.server.node_manager.is_primary:
                        self.server.node_manager.sendreply(payload['blockhash'])
                        self.server.node_manager.replysend['view'] = self.server.node_manager.view
                        self.server.node_manager.replysend['time'] = int(time.time())
                    return
        else:
            self.server.node_manager.asyn[self.server.node_manager.view] = self.server.node_manager.numSeedNode - \
              self.server.node_manager.commitMessages.count(self.server.node_manager.hashcache)

    def handle_sendreply(self, payload):
        print("------handle reply: the start of pre-prepare------")
        # with self.server.node_manager.lock:
        if payload['view'] == self.server.node_manager.view:
            self.server.node_manager.replyMessage += 1
        if (self.server.node_manager.replyMessage > old_div(self.server.node_manager.numSeedNode, 2)) and (not self.server.node_manager.successflag):
            tt = time.time()
            self.server.node_manager.consensus[payload['view']] = [round(tt - self.server.node_manager.timetmp, 3),
                                                                 round(tt - self.server.node_manager.starttime, 3)]
            self.server.node_manager.successflag = True
            self.server.node_manager.replyMessage = 0
            print("next")
            while int(time.time()) < self.server.node_manager.step + self.server.node_manager.starttime:
                time.sleep(1)
            if self.server.node_manager.leadershift:
                self.server.node_manager.sendrequestmessage(payload)
                self.server.node_manager.is_primary = False
            else:
                self.server.node_manager.sendrequest(payload['blockhash'])

    def handle_sendrequestmessage(self,payload):
        self.server.node_manager.is_primary = True
        self.server.node_manager.sendrequest(payload['blockhash'])
        print("changed")

    def handle_sendrequest(self, payload):
        print("------handle request: the start of prepare------")
        self.server.node_manager.starttime = payload["start"]
        # with self.server.node_manager.lock:
        if payload["hash"] != -1:
            if payload["hash"] != self.server.node_manager.blockcache.current_hash:
                self.server.node_manager.failhash.append(payload["newview"]-1)
                self.server.node_manager.fail = True
                # db.write_failhash_to_db(self.server.node_manager.blockchain.wallet.address, payload['newview']-1, payload['hash'])
            else:
                if self.server.node_manager.view >= 1:
                    db.write_to_db(self.server.node_manager.blockchain.wallet.address, self.server.node_manager.blockcache)
                
            print("the hash of last view:")
            print(payload["hash"])
            self.server.node_manager.primary_node_address = payload["address"]

            if self.server.node_manager.view >= 1:
                tmp = time.time()
                if self.server.node_manager.lastblocktime['view'] == self.server.node_manager.view - 1 and self.server.node_manager.lastblocktime['time'] != -1:
                    self.server.node_manager.blocktime[self.server.node_manager.view] = round(tmp - self.server.node_manager.lastblocktime['time'], 3)
                    print('+++handle set block time+++')
                self.server.node_manager.lastblocktime['time'] = tmp
                self.server.node_manager.lastblocktime['view'] = self.server.node_manager.view
                self.server.node_manager.commitMessages = []
                self.server.node_manager.maxTime = 0
                self.server.node_manager.blockchain.received_transactions = \
                  self.server.node_manager.blockchain.received_transactions[len(self.server.node_manager.blockchain.send_transactions):]
                self.server.node_manager.blockchain.current_transactions = \
                  self.server.node_manager.blockchain.current_transactions[self.server.node_manager.txinblock:]
                self.server.node_manager.receivealltx -= self.server.node_manager.receivealltx_last
                # db.clear_unconfirmed_tx_from_disk(self.server.node_manager.blockchain.wallet.address)
                # print "transaction list clear"
                # time.sleep(15)
            self.server.node_manager.view += 1
            if self.server.node_manager.view == payload['newview']:
                print('view check success')
            else:
                print('view check fail')
                self.server.node_manager.view = payload['newview']
            self.server.node_manager.blockchain.lasthash = [payload['newview']-1, payload['hash']]
            # self.server.node_manager.blockchain.send_transactions = deepcopy(self.server.node_manager.blockchain.received_transactions)
            self.server.node_manager.blockchain.send_transactions.clear()
            for tx in self.server.node_manager.blockchain.received_transactions:
                if tx.timestamp < self.server.node_manager.starttime - 1:
                    self.server.node_manager.blockchain.send_transactions.append(tx)
            self.server.node_manager.finishflag = False
            self.server.node_manager.successflag = False
            print("view:", self.server.node_manager.view)
            if (self.server.node_manager.is_committee):
                print("the tx we want to send:")
                print(self.server.node_manager.blockchain.send_transactions)
                self.server.node_manager.sendalltx(self.server.node_manager.blockchain.send_transactions)
                self.server.node_manager.startflag = True
        else:
            print("bft failed, start again")
            print("view:", self.server.node_manager.view)
            self.server.node_manager.GST = payload["GST"]
            self.server.node_manager.primary_node_address = payload["address"]
            self.server.node_manager.commitMessages = []
            self.server.node_manager.maxTime = 0
            self.server.node_manager.blockchain.current_transactions = \
              self.server.node_manager.blockchain.current_transactions[self.server.node_manager.txinblock:]
            # self.server.node_manager.blockchain.send_transactions = deepcopy(self.server.node_manager.blockchain.received_transactions)
            self.server.node_manager.blockchain.send_transactions.clear()
            for tx in self.server.node_manager.blockchain.received_transactions:
                if tx.timestamp < self.server.node_manager.starttime - 1:
                    self.server.node_manager.blockchain.send_transactions.append(tx)
            self.server.node_manager.receivealltx -= self.server.node_manager.receivealltx_last
            self.server.node_manager.finishflag = False
            self.server.node_manager.successflag = False
            if (self.server.node_manager.is_committee):
                self.server.node_manager.sendalltx(self.server.node_manager.blockchain.send_transactions)
                self.server.node_manager.startflag = True
        self.server.node_manager.replyflag = False

    def handle_sendoff(self,payload):
        pass
    
    def handle_sendcorrect(self,payload):
        #找有没有对应的块
        print("------handle send correct------")
        obj = db.get_block_data_by_index(self.server.node_manager.blockchain.get_wallet_address(), payload["hash"])
        print('correct block :', obj)
        if obj:
            self.server.node_manager.sendblock({"block": obj, "address": payload["address"]})
        else:
            self.server.node_manager.sendblock({"block": payload['hash'], "address": payload["address"]})

    def handle_sendblock(self, payload):
        '''
        处理收到的某些缺失view的信息
        '''
        print("---handle send block---")
        self.server.node_manager.receiveblock = True
        if isinstance(payload, Block):
            print(payload)
            idx = payload.index
            self.server.node_manager.failhash.remove(idx)
            del(self.server.node_manager.hash_note[idx])
            db.write_to_db(self.server.node_manager.blockchain.wallet.address, payload)
        else:
            idx = payload
            del(self.server.node_manager.hash_note[idx][0])
            if self.server.node_manager.hash_note[idx]:
                msg_obj = packet.Message("sendcorrect", {"hash":idx, "address": (self.server.node_manager.client.ip,self.server.node_manager.client.port)})
                msg_bytes = pickle.dumps(msg_obj)
                self.server.node_manager.client.sendcorrect(self.server.socket, self.server.node_manager.hash_note[idx][0], msg_bytes)
            else:
                print("cannot find correct")
        if not self.server.node_manager.failhash:
            self.server.node_manager.fail = False


    def handle_sendfailhash(self, payload):
        receive = payload["failhash"]
        for f in self.server.node_manager.failhash:
            if f not in receive:
                self.server.node_manager.hash_note.setdefault(f, []).append(payload["address"])


    # def handle_sendblock(self, payload):
    #     new_block = payload
    #     with self.server.node_manager.lock:
    #         blockchain = self.server.node_manager.blockchain
            
    #         # block_height = db.get_block_height(blockchain.wallet.address)
    #         # latest_block = db.get_block_data_by_index(blockchain.get_wallet_address(), block_height - 1)
            
    #         # 校验交易是否有效
    #         is_valid = True
    #         for idx in range(len(new_block.transactions)):
    #             tx = new_block.transactions[-1 - idx]
    #             if not blockchain.verify_transaction(tx):
    #                 is_valid = False
    #                 break
    #         if is_valid:
    #             self.server.node_manager.blockchain.prepareMessages.append(new_block)
    #             for b in self.server.node_manager.blockchain.prepareMessages:
    #                 count = 0
    #                 for b1 in self.server.node_manager.blockchain.prepareMessages:
    #                     if (b == b1):
    #                         count += 1
    #                 if (count > (self.server.node_manager.numSeedNode) / 3):
    #                     self.server.node_manager.sendchain(new_block)
    #                     print "prepared"        
    #                     return
                
                   

    # def handle_sendchain(self, payload):
    #     new_block = payload
    #     with self.server.node_manager.lock:
    #         blockchain = self.server.node_manager.blockchain
            
    #         # block_height = db.get_block_height(blockchain.wallet.address)
    #         # latest_block = db.get_block_data_by_index(blockchain.get_wallet_address(), block_height - 1)
            
    #         # 校验交易是否有效
    #         is_valid = True
    #         for idx in range(len(new_block.transactions)):
    #             tx = new_block.transactions[-1 - idx]
    #             if not blockchain.verify_transaction(tx):
    #                 is_valid = False
    #                 break
    #         if is_valid:
    #             self.server.node_manager.blockchain.commitMessages.append(new_block)
    #             for b in self.server.node_manager.blockchain.commitMessages:
    #                 count = 0
    #                 for b1 in self.server.node_manager.blockchain.commitMessages:
    #                     if (b == b1):
    #                         count += 1
    #                 if (count > (2*self.server.node_manager.numSeedNode) / 3):
    #                     db.write_to_db(blockchain.wallet.address, new_block)
    #                     print "committed"
    #                     return
                    

            # if (latest_block.current_hash == new_block.previous_hash) and (latest_block.index + 1 == new_block.index):

            #     # 校验交易是否有效
            #     is_valid = True
            #     for idx in range(len(new_block.transactions)):
            #         tx = new_block.transactions[-1 - idx]
            #         if not blockchain.verify_transaction(tx):
            #             is_valid = False
            #             break

            #     if is_valid:
            #         db.write_to_db(blockchain.wallet.address, new_block)
            #         # 重新挖矿
            #         blockchain.current_transactions = []
            #         db.clear_unconfirmed_tx_from_disk(blockchain.wallet.address)
            # else:
            #     self.add_to_candidate_blocks(blockchain, new_block)

            # blockchain.set_consensus_chain()

    def handle_version(self, payload):
        version = payload.version
        if version != 1:
            # 版本不一样，拒绝
            print('[Warn] invalid version, ignore!!')
            pass
        else:
            client_ip, client_port = self.client_address
            client_node_id = payload.from_id
            new_node = Node(client_ip, client_port, client_node_id)
            new_node.version = 1
            self.server.node_manager.buckets.insert(new_node)
            blockchain = self.server.node_manager.blockchain

            block_counts = db.get_block_height(blockchain.get_wallet_address())
            verack = Verack(1, int(time.time()), self.server.node_manager.node_id, client_node_id,
                            block_counts)
            self.server.node_manager.sendverck(new_node, verack)

            if payload.best_height > block_counts:
                # TODO 检查best_height，同步区块链
                pass

    def handle_verack(self, payload):
        version = payload.version
        if version != 1:
            # 版本不一样，拒绝
            print('[Warn] invalid version, ignore!!')
            pass
        else:
            client_node_id = payload.from_id
            client_ip, client_port = self.client_address
            new_node = Node(client_ip, client_port, client_node_id)
            new_node.version = 1
            self.server.node_manager.buckets.insert(new_node)
            blockchain = self.server.node_manager.blockchain

            if payload.best_height > db.get_block_height(blockchain.get_wallet_address()):
                # TODO 检查best_height，同步区块链
                pass

    def add_to_candidate_blocks(self, blockchain, new_block):
        if new_block.index in list(blockchain.candidate_blocks.keys()):
            blockchain.candidate_blocks[new_block.index].add(new_block)
        else:
            blockchain.candidate_blocks[new_block.index] = set()
            blockchain.candidate_blocks[new_block.index].add(new_block)


class Server(socketserver.ThreadingUDPServer):
    """
    接收消息，并做相应处理
    """

    def __init__(self, address, handler):
        socketserver.UDPServer.__init__(self, address, handler)
        self.lock = threading.Lock()


class Node(object):
    """
    P2P网络的节点，发送消息。实现Kad中的PING、FIND_NODE、FIND_VALUE和STORE消息
    """

    def __init__(self, ip, port, client_node_id):
        self.ip = ip
        self.port = port
        self.node_id = client_node_id
        self.version = None

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __eq__(self, other):
        if self.__class__ == other.__class__ \
                and self.ip == other.ip \
                and self.port == other.port \
                and self.node_id == other.node_id:
            return True
        return False

    def triple(self):
        return (self.ip, self.port, self.node_id)

    def ping(self, sock, target_node_address, message):
        sock.sendto(zlib.compress(message), target_node_address)

    def pong(self, sock, target_node_address, message):
        sock.sendto(zlib.compress(message), target_node_address)

    def find_neighbors(self, sock, target_node_address, message):
        sock.sendto(zlib.compress(message), target_node_address)

    def found_neighbors(self, sock, target_node_address, message):
        sock.sendto(zlib.compress(message), target_node_address)

    def find_value(self, sock, target_node_address, message):
        sock.sendto(zlib.compress(message), target_node_address)

    def found_value(self, sock, target_node_address, message):
        sock.sendto(zlib.compress(message), target_node_address)

    def store(self, sock, target_node_address, message):
        sock.sendto(zlib.compress(message), target_node_address)

    def sendrequestmessage(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)
    
    def sendrequest(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)

    def sendtx(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)

    def sendalltx(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)

    def sendblockhash(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)

    def sendreply(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)

    def sendblock(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)

    def sendfailhash(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)

    def sendcorrect(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)

    def sendoff(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)

    def sendversion(self, sock, target_node_address, message):
        sock.sendto(zlib.compress(message), target_node_address)

    def sendverack(self, sock, target_node_address, message):
        sock.sendto(zlib.compress(message), target_node_address)


class NodeManager(object):
    """
    P2P网络中每个节点同时提供Server和Client的作用

    节点之间互相通信(发送+接收)，实现的kad协议算法的4中操作，分别是：
    1.PING：检测节点是否在线
    2.STORE：在某个节点上存储key、value
    3.FIND NODE：返回对方节点桶中距离请求key最近的k个节点
    4.FIND VALUE：与FIND NODE类似，不过返回的是相应key的value

    """

    def __init__(self, ip, port=0, genisus_node=False, is_committee_node=False, 
                    leader_shift=False, expected_client_num=4, isServer=False):
        self.ip = ip
        self.port = port
        self.node_id = self.__random_id()
        self.address = (self.ip, self.port)
        self.buckets = KBucketSet(self.node_id)
        self.is_committee = is_committee_node
        self.is_primary = genisus_node
        self.expectedClientNum = expected_client_num
        self.leadershift = leader_shift
        
        self.view = 0 #轮次
        
        self.receivealltx_last = 0
        self.receivealltx = 0
        self.txinblock = 0
        self.maxTime = 0
        self.committee_member = []
        # self.prepareMessages = []
        self.commitMessages = []
        self.hashcache = 0
        self.blockcache = Block(0,0,0,0,0)
        self.primary_node_address = self.address
        self.starttime = 0
        self.replyMessage = 0
        
        self.GST = 1
        self.step = 5
        
        self.startflag = False #是否开始出块
        self.replyflag = False
        self.finishflag = False #是否收到法定个哈希并sendreply
        self.successflag = False
        self.receiveblock = True
        self.failhash = []
        self.hash_note = {} # 记录收到的failhash以寻找可以请求正确区块的节点
        self.fail = False
        self.failhashsend = True
        
        self.asyn = {}

        self.consensus = {}
        self.timetmp = 0

        self.blocktime = {}
        self.lastblocktime = {'view': -1, "time": -1}

        self.replysend = {'view': -1, 'time': -1}
        self.disconnect = 0

        # 每个消息都有一个唯一的rpc_id，用于标识节点之间的通信（该rpc_id由发起方生成，并由接收方返回），
        # 这样可以避免节点收到多个从同一个节点发送的消息时无法区分
        self.rpc_ids = {}  # rpc_ids被多个线程共享，需要加锁

        self.lock = threading.Lock()  # 备注，由于blockchain数据被多个线程共享使用（矿工线程、消息处理线程），需要加锁

        self.server = Server(self.address, ProcessMessages)
        self.port = self.server.server_address[1]
        self.client = Node(self.ip, self.port, self.node_id)
        self.data = {}

        self.alive_nodes = {}  # {"xxxx":"2018-03-12 22:00:00",....}

        self.server.node_manager = self
        self.blockchain = Blockchain(genisus_node)
        self.numSeedNode = 0

        self.errorflag = True

        # 消息处理
        self.processmessages_thread = threading.Thread(target=self.server.serve_forever)
        self.processmessages_thread.daemon = True
        self.processmessages_thread.start()

        # 消息发送 TODO
        # self.sendmessages_thread = threading.Thread(target=self.sendmessages)
        # self.sendmessages_thread.daemon = True
        # self.sendmessages_thread.start()

        self.minner_thread = threading.Thread(target=self.minner)
        self.minner_thread.daemon = True
        if not isServer:
            self.start()

        print('[Info] start new node', self.ip, self.port, self.node_id)

    def start(self):
        # 矿工线程
        print("start protocol")
        if self.is_committee:
            self.minner_thread.start()

    def ping(self, sock, server_node_id, target_node_address):
        payload = packet.Ping(self.node_id, server_node_id)
        msg_obj = packet.Message("ping", payload)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.ping(sock, target_node_address, msg_bytes)

    def pong(self, sock, server_node_id, target_node_address):
        """
        发送对ping请求的响应消息
        :param sock: Server端监听返回的客户端连接
        :param target_node_address: 目标节点的地址
        :return:
        """
        payload = packet.Pong(self.node_id, server_node_id)
        msg_obj = packet.Message("pong", payload)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.pong(sock, target_node_address, msg_bytes)

    def find_neighbors(self, node_id, rpc_id, sock, server_node_id, server_node_address):
        payload = packet.FindNeighbors(node_id, self.node_id, server_node_id, rpc_id)
        msg_obj = packet.Message("find_neighbors", payload)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.find_neighbors(sock, server_node_address, msg_bytes)

    def found_neighbors(self, node_id, rpc_id, neighbors, sock, server_node_id, server_node_address):
        payload = packet.FoundNeighbors(node_id, self.node_id, server_node_id, rpc_id, neighbors)
        msg_obj = packet.Message("found_neighbors", payload)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.found_neighbors(sock, server_node_address, msg_bytes)

    def find_value(self, key, rpc_id, sock, server_node_id, target_node_address):
        payload = packet.FindValue(key, self.node_id, server_node_id, rpc_id)
        msg_obj = packet.Message("find_value", payload)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.find_value(sock, target_node_address, msg_bytes)

    def found_value(self, key, value, rpc_id, sock, server_node_id, target_node_address):
        payload = packet.FoundValue(key, value, self.node_id, server_node_id, rpc_id)
        msg_obj = packet.Message("found_value", payload)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.found_value(sock, target_node_address, msg_bytes)

    def store(self, key, value, sock, server_node_id, target_node_address):
        payload = packet.Store(key, value, self.node_id, server_node_id)
        msg_obj = packet.Message("store", payload)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.store(sock, target_node_address, msg_bytes)

    def iterative_find_nodes(self, key, seed_node=None):
        """
        找到距离目标节点最近的K个节点
        :param server_node_id:
        :param seed_nodes:
        :return:
        """
        k_nearest_nodes_util = KNearestNodesUtil(key)
        k_nearest_nodes_util.update(self.buckets.nearest_nodes(key))
        if seed_node:
            rpc_id = self.__get_rpc_id()
            self.rpc_ids[rpc_id] = k_nearest_nodes_util
            self.find_neighbors(key, rpc_id, self.server.socket, key,
                                (seed_node.ip, seed_node.port))

        while (not k_nearest_nodes_util.is_complete()) or seed_node:  # 循环迭代直至距离目标节点最近的K个节点都找出来
            # 限制同时向ALPHA(3)个邻近节点发送FIND NODE请求
            unvisited_nearest_nodes = k_nearest_nodes_util.get_unvisited_nearest_nodes(constant.ALPHA)
            for node in unvisited_nearest_nodes:
                k_nearest_nodes_util.mark(node)
                rpc_id = self.__get_rpc_id()
                self.rpc_ids[rpc_id] = k_nearest_nodes_util
                self.find_neighbors(key, rpc_id, self.server.socket, key,
                                    (node.ip, node.port))
            time.sleep(1)
            seed_node = None

        return k_nearest_nodes_util.get_result_nodes()

    def iterative_find_value(self, key):
        k_nearest_nodes_util = KNearestNodesUtil(key)
        k_nearest_nodes_util.update(self.buckets.nearest_nodes(key))
        while not k_nearest_nodes_util.is_complete():
            # 限制同时向ALPHA(3)个邻近节点发送FIND NODE请求
            unvisited_nearest_nodes = k_nearest_nodes_util.get_unvisited_nearest_nodes(constant.ALPHA)
            for node in unvisited_nearest_nodes:
                k_nearest_nodes_util.mark(node)
                rpc_id = self.__get_rpc_id()
                self.rpc_ids[rpc_id] = k_nearest_nodes_util
                self.find_value(key, rpc_id, self.server.socket, node.node_id, (node.ip, node.port))

            time.sleep(1)

        return k_nearest_nodes_util.get_target_value()

    def bootstrap(self, seed_nodes=[]):
        """
        根据初始节点引导初始化
        :param seed_nodes:<Node list> 种子节点列表
        :return:
        """
        self.committee_member = seed_nodes

        for seed_node in seed_nodes:
            # 握手
            self.sendversion(seed_node,
                             Version(1, int(time.time()), self.node_id, seed_node.node_id,
                                     db.get_block_height(self.blockchain.get_wallet_address())))

        for seed_node in seed_nodes:
            self.iterative_find_nodes(self.client.node_id, seed_node)

        if len(seed_nodes) == 0:
            for seed_node in self.buckets.get_all_nodes():
                self.iterative_find_nodes(self.client.node_id, seed_node)
        
        self.numSeedNode = len(seed_nodes)

    def __hash_function(self, key):
        return int(hashlib.md5(key.encode('ascii')).hexdigest(), 16)

    def __get_rpc_id(self):
        return random.getrandbits(constant.BITS)

    def __random_id(self):
        return random.randint(0, (2 ** constant.BITS) - 1)

    def hearbeat(self, node, bucket, node_idx):
        # buckets在15分钟内节点未改变过需要进行refresh操作（对buckets中的每个节点发起find node操作）
        # 如果所有节点都有返回响应，则该buckets不需要经常更新
        # 如果有节点没有返回响应，则该buckets需要定期更新保证buckets的完整性
        node_id = node.node_id
        ip = node.ip
        port = node.port

        tm = int(time.time())
        if tm - int(self.alive_nodes[node_id]) > 1800:
            # 节点的更新时间超过1min，认为已下线，移除该节点
            bucket.pop(node_idx)
            self.alive_nodes.pop(node_id)

        # print '[Info] heartbeat....'
        self.ping(self.server.socket, node_id, (ip, port))

    def minner(self):
        # member_index = 0
        while True:
            # blockchain多个线程共享使用，需要加锁
            
            if self.view == 0 and self.is_primary:
                # time.sleep(30) # 用 run + simulation 运行时根据节点数量设置相应大的等待时间
                if len(self.blockchain.received_transactions) > 3:
                    print("-------START--------")
                    self.sendrequest(0)

            if not (not self.startflag or self.receivealltx < len(self.committee_member)-1 or # 
                    int(time.time()) <= self.maxTime):
                print("-------collected enough tx: the start of commit-------")
                # with self.lock:
                print('current:', len(self.blockchain.current_transactions))
                self.timetmp = time.time()
                self.receivealltx_last = self.receivealltx
                self.txinblock = len(self.blockchain.current_transactions)
                # print "txinblock", self.txinblock
                new_block = self.blockchain.do_mine(self.view, self.starttime)
                self.blockcache = new_block
                self.sendblockhash(new_block.current_hash)
                self.startflag = False

            if self.replyflag and self.is_primary and (int(time.time())>self.replytime + 10):
                print("++++++++++BFT FAILED++++++++++")
                self.sendrequest(-1)

            # if self.failhash and self.receiveblock:
            #     self.receiveblock = False
            #     print("------send correct------")
            #     node = self.committee_member[member_index]
            #     msg_obj = packet.Message("sendcorrect", {"hash":self.failhash[0], "address": (self.client.ip,self.client.port)})
            #     msg_bytes = pickle.dumps(msg_obj)
            #     self.client.sendcorrect(self.server.socket, (node.ip, node.port), msg_bytes)
            #     member_index += 1

            if self.view % 5 == 0 and self.failhashsend:
                self.failhashsend = False
                self.sendfailhash(self.failhash)
                
            if self.view % 5 == 1 and not self.failhashsend:
                self.failhashsend = True
                for f in self.hash_note:     
                    msg_obj = packet.Message("sendcorrect", {"hash":f, "address": (self.client.ip,self.client.port)})
                    msg_bytes = pickle.dumps(msg_obj)
                    self.client.sendcorrect(self.server.socket, self.hash_note[f][0], msg_bytes)            

            # if self.replysend['view'] == self.view and int(time.time()) > self.replysend['time'] + 10:
            #     for node in self.committee_member:
            #         msg_obj = packet.Message("sendoff", self.view)
            #         msg_bytes = pickle.dumps(msg_obj)
            #         self.client.sendoff(self.server.socket, (node.ip, node.port), msg_bytes)

            time.sleep(.1)
            
            # if self.is_primary:
            #     print "request"
            #     self.sendrequest()
            #     print "pre-prepared"
            #     self.startflag = True

            # if self.startflag:
            #     self.sendalltx(self.blockchain.current_transactions)
            #     print "prepared"
            #     time.sleep(20)
            #     print self.blockchain.current_transactions
            #     try:
            #         with self.lock:
            #             new_block = self.blockchain.do_mine()
            #             self.sendchain(new_block)
            #             print "committed"

            #     except Error as e:
            #         pass
            #     self.receivetx = 0
            #     self.startflag = False

            # self.blockchain.set_consensus_chain()  # pow机制保证最长辆（nonce之和最大的链）

    def set_data(self, key, value):
        """
        数据存放:
        1.首先发起节点定位K个距离key最近的节点
        2.发起节点对这K个节点发送STORE消息
        3.收到STORE消息的K个节点保存(key, value)数据

        :param key:
        :param value:
        :return:
        """
        data_key = self.__hash_function(key)
        k_nearest_ndoes = self.iterative_find_nodes(data_key)
        if not k_nearest_ndoes:
            self.data[str(data_key)] = value
        for node in k_nearest_ndoes:
            self.store(data_key, value, self.server.socket, node.node_id, (node.ip, node.port))

    def get_data(self, key):
        """
        读取数据
        1.当前节点收到查询数据的请求(获取key对应的value)
        2.当前节点首先检测自己是否保存了该数据，如果有则返回key对应的value
        3.如果当前节点没有保存该数据，则计算获取距离key值最近的K个节点，分别向这K个节点发送FIND VALUE的操作进行查询
        4.收到FIND VALUE请求操作的节点也进行上述(2)~(3)的过程（递归处理）
        :param key:
        :param value:
        :return:
        """
        data_key = self.__hash_function(key)
        if str(data_key) in self.data:
            return self.data[str(data_key)]
        value = self.iterative_find_value(data_key)
        if value:
            return value
        else:
            raise KeyError

    def sendrequestmessage(self,payload):
        print("change sent")
        node = self.committee_member[0]
        msg_obj = packet.Message("sendrequestmessage", payload)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.sendrequestmessage(self.server.socket, (node.ip, node.port), msg_bytes)
    
    
    def sendrequest(self,payload):
        """
        广播一個request消息
        :param payload 上一轮commit的hash:
        :return:
        """
        print("-------send request: the end of pre-prepare-------")
        if payload != -1:
            self.starttime = int(time.time()) #主节点记录轮次开始时间
            if payload != self.blockcache.current_hash:
                self.failhash.append(self.view)
                self.fail = True
                # db.write_failhash_to_db(self.blockchain.wallet.address, self.view, payload)
            else:
                # print "pre-prepared1"
                # 自身确认入链
                if self.view >= 1:
                    db.write_to_db(self.blockchain.wallet.address, self.blockcache)
                    print("blockcache :", self.blockcache)
            tmp = time.time()
            if self.lastblocktime['view'] == self.view - 1 and self.lastblocktime['time'] != -1:
                self.blocktime[self.view] = round(tmp - self.lastblocktime['time'], 3)
                print('++++set block time+++')
            self.lastblocktime['time'] = tmp
            self.lastblocktime['view'] = self.view
            if self.view >=1:
                self.commitMessages = []
                self.maxTime = 0
                self.blockchain.received_transactions = self.blockchain.received_transactions[len(self.blockchain.send_transactions):]
                self.blockchain.current_transactions = self.blockchain.current_transactions[self.txinblock:]
                self.receivealltx -= self.receivealltx_last
            # self.blockchain.send_transactions=deepcopy(self.blockchain.received_transactions)
            self.blockchain.send_transactions.clear()
            for tx in self.blockchain.received_transactions:
                if tx.timestamp < self.starttime - 1:
                    self.blockchain.send_transactions.append(tx)
            # print "transaction list reset"
            self.blockchain.lasthash = [self.view, payload]
            self.view += 1
            self.successflag = False
            print("view:", self.view)
            for node in self.committee_member:    
                msg_obj = packet.Message("sendrequest", 
                  {"hash":payload, "address": (self.client.ip,self.client.port), "start": self.starttime, 'newview': self.view})
                msg_bytes = pickle.dumps(msg_obj)
                self.client.sendrequest(self.server.socket, (node.ip, node.port), msg_bytes)
            # print "++++++++++++++sendrequest&tx++++++++++++++++"
            self.sendalltx(self.blockchain.send_transactions)
            self.startflag = True
            # print "pre-prepared2"
        else:
            self.GST += 1
            self.starttime = int(time.time())
            for node in self.committee_member:    
                msg_obj = packet.Message("sendrequest", 
                  {"hash":payload, "address": (self.client.ip, self.client.port), "start": self.starttime, 'newview': self.view, "GST": self.GST})
                msg_bytes = pickle.dumps(msg_obj)
                self.client.sendrequest(self.server.socket, (node.ip, node.port), msg_bytes)
            self.commitMessages = []
            self.replyMessage = 0
            self.maxTime = 0
            self.blockchain.current_transactions = self.blockchain.current_transactions[self.txinblock:]
            # self.blockchain.send_transactions = deepcopy(self.blockchain.received_transactions)
            self.blockchain.send_transactions.clear()            
            for tx in self.blockchain.received_transactions:
                if tx.timestamp < self.starttime - 1:
                    self.blockchain.send_transactions.append(tx)
            self.receivealltx -= self.receivealltx_last
            # print "transaction list reset"
            self.successflag = False
            print("view:", self.view)
            # print "++++++++++++++sendrequest&tx++++++++++++++++"
            self.sendalltx(self.blockchain.send_transactions)
            self.startflag = True
            # print "pre-prepared2"
        self.replyflag = False
        self.finishflag = False

    def sendtx(self, tx):
        """
        广播一個交易
        :param tx:
        :return:
        """
        # data_key = self.__hash_function(tx.txid)
        # k_nearest_ndoes = self.iterative_find_nodes(data_key)
        # if not k_nearest_ndoes:
        #     self.data[data_key] = tx
        # for node in k_nearest_ndoes:
        #     tx.from_id = self.node_id
        #     msg_obj = packet.Message("sendtx", tx)
        #     msg_bytes = pickle.dumps(msg_obj)
        #     self.client.sendtx(self.server.socket, (node.ip, node.port), msg_bytes)
        #     break
        # new_tx = tx
        # with self.lock:
        #     blockchain = self.blockchain
        #     # 判断区块中是否存在
        #     if blockchain.find_transaction(new_tx.txid):
        #         return
        #     # 判断交易池中是否存在
        #     for k in range(len(blockchain.received_transactions)):
        #         uncomfirmed_tx = blockchain.received_transactions[-1 - k]
        #         if uncomfirmed_tx.txid == new_tx.txid:
        #             return
            # blockchain.current_transactions.append(new_tx)
            # blockchain.received_transactions.append(new_tx)
            # db.write_unconfirmed_tx_to_db(blockchain.wallet.address, new_tx)
        print("...")

    def sendalltx(self, alltx):
        print("------send alltx: the end of prepare------")
        # print "before sendalltx"
        # print "send tx:", len(self.blockchain.send_transactions)
        # print "received tx:", len(self.blockchain.received_transactions)
        # print "current tx:", len(self.blockchain.current_transactions)
        tm = int(time.time())
        for node in self.committee_member:
            print("sendalltx to ", (node.ip, node.port))
            msg_obj = packet.Message("sendalltx", {"alltx":alltx, "time":tm})
            msg_bytes = pickle.dumps(msg_obj)
            self.client.sendalltx(self.server.socket, (node.ip, node.port), msg_bytes)
            
        for new_tx in alltx:
            self.blockchain.current_transactions.append(new_tx)
        # print "sendalltx"
        # print "send tx:", len(self.blockchain.send_transactions)
        # print "received tx:", len(self.blockchain.received_transactions)
        # print "current tx:", len(self.blockchain.current_transactions)

    def sendblockhash(self, blockhash):
        """
        广播一个blockhash
        :param blockhash:
        :return:
        """
        print("------send blockhash: the end of commit------")
        print("blockhash :", blockhash)
        for node in self.committee_member:
            msg_obj = packet.Message("sendblockhash", {'blockhash': blockhash, 'view': self.view})
            msg_bytes = pickle.dumps(msg_obj)
            self.client.sendblockhash(self.server.socket, (node.ip, node.port), msg_bytes)
            # error test
            # if self.view == 3 and self.errorflag:
            #     self.errorflag = False
            #     break
        if self.is_primary:
            self.replyflag = True
            self.replytime = int(time.time())
        # error test
        if self.view == 3 and self.is_primary:
            self.blockcache.current_hash += '1'
            

    def sendreply(self, blockhash):
        print("------send reply: the end of reply------")
        msg_obj = packet.Message("sendreply", {'blockhash': blockhash, 'view': self.view})
        msg_bytes = pickle.dumps(msg_obj)
        print("primary_node_address:")
        print(self.primary_node_address)
        self.client.sendreply(self.server.socket, self.primary_node_address, msg_bytes)

   
    def sendblock(self,payload):
        print("----send block----")
        msg_obj = packet.Message("sendblock", payload["block"])
        msg_bytes = pickle.dumps(msg_obj)
        self.client.sendblock(self.server.socket, payload["address"], msg_bytes)


    def sendfailhash(self,payload):
        print('+++ send fail hash +++')
        for node in self.committee_member:
            msg_obj = packet.Message("sendfailhash", {'failhash': payload, 'address': (self.client.ip, self.client.port)})
            msg_bytes = pickle.dumps(msg_obj)
            self.client.sendalltx(self.server.socket, (node.ip, node.port), msg_bytes)
    
    
    # def sendblock(self, block):
    #     """
    #     广播一个block
    #     :param block:
    #     :return:
    #     """
    #     data_key = self.__hash_function(block.current_hash)
    #     k_nearest_ndoes = self.iterative_find_nodes(data_key)
    #     if not k_nearest_ndoes:
    #         self.data[data_key] = block
    #     for node in k_nearest_ndoes:
    #         block.from_id = self.node_id
    #         msg_obj = packet.Message("sendblock", block)
    #         msg_bytes = pickle.dumps(msg_obj)
    #         print '[Info] send block', node.ip, node.port, block.current_hash
    #         self.client.sendblock(self.server.socket, (node.ip, node.port), msg_bytes)

    # def sendchain(self, block):
    #     """
    #     广播一个hashed block
    #     :param block:
    #     :return:
    #     """
    #     data_key = self.__hash_function(block.current_hash)
    #     k_nearest_ndoes = self.iterative_find_nodes(data_key)
    #     if not k_nearest_ndoes:
    #         self.data[data_key] = block
    #     for node in k_nearest_ndoes:
    #         block.from_id = self.node_id
    #         msg_obj = packet.Message("sendchain", block)
    #         msg_bytes = pickle.dumps(msg_obj)
    #         print '[Info] send hashed block', node.ip, node.port, block.current_hash
    #         self.client.sendchain(self.server.socket, (node.ip, node.port), msg_bytes)

    def sendversion(self, node, version):
        msg_obj = packet.Message("version", version)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.sendversion(self.server.socket, (node.ip, node.port), msg_bytes)

    def sendverck(self, node, verack):
        msg_obj = packet.Message("verack", verack)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.sendverack(self.server.socket, (node.ip, node.port), msg_bytes)

    # def sendmessages(self):
    #     while True:
    #         for bucket in self.buckets.buckets:
    #             for i in range(len(bucket)):
    #                 node = bucket[i]
    #                 # 要先完成握手才可以进行其他操作
    #                 if node.version == None:
    #                     continue
    #
    #                     # hearbeat
    #                     # self.hearbeat(node, bucket, i)
    #
    #                     # 发送addr消息，告诉对方节点自己所拥有的节点信息
    #                     # TODO
    #
    #                     # 发送getaddr消息，获取尽量多的节点
    #                     # TODO
    #
    #                     # 发送inv消息，请求一个区块哈希的列表
    #                     # TODO
    #
    #                     # 发送getdata消息，用于请求某个块或交易的完整信息
    #                     # TODO
    #
    #         time.sleep(10)
