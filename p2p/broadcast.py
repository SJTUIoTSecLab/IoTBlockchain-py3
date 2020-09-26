# coding:utf-8
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import object
import hashlib   #hash算法库
import json      #json格式转换库
import socketserver   #socketserver模块，实现服务器模块的相关功能
import pickle     #pickle提供了一个简单的持久化功能。可以将对象以文件的形式存放在磁盘上。
import threading   #锁模块
import random

import time
from binascii import Error  #binascii用来进行进制和字符串之间的转换

import zlib              #zlib模块作用：压缩数据存放在硬盘或内存等设备

import db               #数据库模块
from blockchain import Blockchain   
from p2p import constant
from p2p.kbucketset import KBucketSet
from p2p.nearestnodes import KNearestNodesUtil
from p2p import packet
from p2p.packet import Version
from p2p.LSP import LSP


class ProcessMessages(socketserver.BaseRequestHandler):#继承SocketServer.BaseRequestHandler
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
        msg_obj = pickle.loads(zlib.decompress(self.request[0]))#翻译request

        command = msg_obj.payloadcommand = msg_obj.command
        payload = msg_obj.payloadcommand = msg_obj.payload


        if command=="lspr":                   #收到lspr命令
            self.handle_LSPR(payload)
        elif command=="respoflspr" :#收到了对lspr命令的回复，即一组lsp
            self.handle_RESP(payload)
        elif command=="routetable":#收到了广播节点下发的路由表
            self.handle_ROUTE(payload)
        elif command=="broadcast":#各节点收到了源节点的广播
            self.handle_BROADCAST(payload)
        elif command == "version":
            self.handle_version(payload)
        elif command == "sendtx":
            self.handle_sendtx(payload)
                                                   


    #处理各种命令
    def handle_LSPR(self,payload):#处理收到的lspr命令，最好能判别是否已经处理过一次lspr	
	#print "received lspr"
	sorceport=payload.sorceport
        sorceip=payload.sorceip
        socket=self.server.socket
        #target_adress应该是(client_ip,client_port)的形式 元组数据类型
	if self.server.node_manager.tablsp.flag==0:
		if sorceport!=self.server.node_manager.tablsp.basetable[1]:
			self.server.node_manager.tablsp.flag=1
        		self.server.node_manager.lspr((sorceip,sorceport))#向给自己发送lspr的点发送信息(自己的lsp),并且将自己的flag设为１
        		self.server.node_manager.asklsp([sorceip,sorceport])#向自己路由表中的节点发送,需要在其他节点
        


    def handle_RESP(self,payload):#收到许多含有lsp的消息，处理这样的消息todo
	lsp=payload.lsp
	#print "mark lsp in broad node"
	#print lsp
	self.server.node_manager.tablsp.lspgroup.append(lsp)#将得到的lsp放入lspgroup中
	#判断什么时候能计算最小生成树
	k=len(self.server.node_manager.tablsp.lspgroup)

	if k>8:#k满足要求可以进入广播  tochange
		# 进行生成树的计算,在节点中储存这棵树
		self.server.node_manager.tablsp.dictlspfun()#生成字典
		dictlsp=self.server.node_manager.tablsp.dictlsp
		tree=self.server.node_manager.tablsp.solvetree()#最小生成树矩阵
		message=self.server.node_manager.tablsp.message
		self.server.node_manager.broadcast(message,tree,dictlsp)
		#告诉其他节点要传播的信息以及最小生成树
		



    def handle_BROADCAST(self,payload):#收到了广播，按指派的路由表广播
	#if 是测试用的
	if not self.server.node_manager.tablsp.message:
        	tree=payload.tree
        	message=payload.message
		dictlsp=payload.dictlsp
        	#将广播信息计入本节点
		print("here port:")
		print(self.server.node_manager.tablsp.basetable[1])
		self.server.node_manager.tablsp.addmessage(message)
		print(self.server.node_manager.tablsp.message)
        	self.server.node_manager.broadcast(message,tree,dictlsp)

    def handle_version(self, payload):
        version = payload.version
        if version != 1:
            # 版本不一样，拒绝
            print('[Warn] invalid version, ignore!!') 
            pass
        else:
	    d=payload.distance
            client_ip, client_port = self.client_address
            client_node_id = payload.from_id
            new_node = Node(client_ip, client_port, client_node_id)
            new_node.version = 1
            self.server.node_manager.tablsp.insert(new_node)
	    self.server.node_manager.tablsp.neighbourdistance.append(d)
            # blockchain = self.server.node_manager.blockchain

            # block_counts = db.get_block_height(blockchain.get_wallet_address())
            # verack = Verack(1, int(time.time()), self.server.node_manager.node_id, client_node_id,  ##消息反馈
            #                 block_counts)
            # self.server.node_manager.sendverck(new_node, verack)

            #if payload.best_height > block_counts:
                # TODO 检查best_height，同步区块链
             #   pass
        
    def handle_sendtx(self, payload):
        new_tx = payload
        with self.server.node_manager.lock:
            blockchain = self.server.node_manager.blockchain

        # 判断区块中是否存在
        if blockchain.find_transaction(new_tx.txid):
            return
        # 判断交易池中是否存在
        for k in range(len(blockchain.current_transactions)):
            uncomfirmed_tx = blockchain.current_transactions[-1 - k]
            if uncomfirmed_tx.txid == new_tx.txid:
                return

        blockchain.current_transactions.append(new_tx)
        db.write_unconfirmed_tx_to_db(blockchain.wallet.address, new_tx)

    

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
        

    def respoflspr(self,sock,target_node_address,message):#以SOCK为通信端口，向target发送message(lsp)
        sock.sendto(zlib.compress(message),target_node_address)

    def asklsp(self,sock,target_node_address,message):#告诉其他节点自己需要汇总lsp
        sock.sendto(zlib.compress(message),target_node_address)

    def broadcast(self,sock,target_node_address,message):#向其他节点发送广播
        sock.sendto(zlib.compress(message),target_node_address) 
    
    def sendversion(self, sock, target_node_address, message):
        sock.sendto(zlib.compress(message), target_node_address)

    def sendtx(self, sock, target_node_address, message):
        ret = sock.sendto(zlib.compress(message), target_node_address)


class NodeManager(object):
    """
    P2P网络中每个节点同时提供Server和Client的作用

    节点之间互相通信(发送+接收)，实现的kad协议算法的4中操作，分别是：
    1.PING：检测节点是否在线
    2.STORE：在某个节点上存储key、value
    3.FIND NODE：返回对方节点桶中距离请求key最近的k个节点
    4.FIND VALUE：与FIND NODE类似，不过返回的是相应key的value

    """

    def __init__(self, ip, port=0, genisus_node=False):
        self.ip = ip
        self.port = port
        self.node_id = self.__random_id()#可能会分配到相同的id待解决
        self.address = (self.ip, self.port)
	
        self.tablsp=LSP(self.address,self.node_id)#每个节点储存的LSP表  todo
        self.rpc_ids = {}  # rpc_ids被多个线程共享，需要加锁

        self.lock = threading.Lock()  # 备注，由于blockchain数据被多个线程共享使用（矿工线程、消息处理线程），需要加锁

        self.server = Server(self.address, ProcessMessages)#处理类使用processmessage的SERVER
        self.port = self.server.server_address[1]
        self.client = Node(self.ip, self.port,self.node_id)
        self.data = {}

        self.alive_nodes = {}  # {"xxxx":"2018-03-12 22:00:00",....}

        self.server.node_manager = self
        self.blockchain = Blockchain(genisus_node)

        # 消息处理
        self.processmessages_thread = threading.Thread(target=self.server.serve_forever)
        self.processmessages_thread.daemon = True
        self.processmessages_thread.start()

        # 消息发送 TODO
        # self.sendmessages_thread = threading.Thread(target=self.sendmessages)
        # self.sendmessages_thread.daemon = True
        # self.sendmessages_thread.start()

        # 矿工线程
        self.minner_thread = threading.Thread(target=self.minner)
        self.minner_thread.daemon = True
        self.minner_thread.start()

        print('[Info] start new node', self.ip, self.port)

    def lspr(self,target_node_address):#发送自己的lsp给广播节点
        ##发送自己的lsp给广播
        payload=packet.lsp(self.tablsp)#打包lsp的信息
        msg_obj=packet.Message("respoflspr",payload)#表示这是对lspr的回复
        msg_bytes=pickle.dumps(msg_obj)
	sock=self.server.socket
        self.client.respoflspr(sock,target_node_address,msg_bytes)        


    

    def broadcast(self,context,tree,dictlsp):
        
	
	print("mark dictlsp")
	print(dictlsp)
	child=self.tablsp.findkids(dictlsp,tree)#先用这个数组测试功能
	tree=self.tablsp.deletenode(tree,dictlsp)#删除该节点作为子节点的子节点的情况
	print("mark 删除后的树")
	print(tree)
	payload=packet.broadcast(context,tree,dictlsp)
        msg_obj=packet.Message("broadcast",payload)
        msg_bytes=pickle.dumps(msg_obj)
	
        x=0 #用于记录这个路由的位置
	k=len(child)
        #根据Id找到对应的路由信息
	#找到对应的ip,port
        for i in range(k):
	    ip=child[i][0]
	    port=child[i][1]
            target_node_address=(ip,port)
            #按路由发送广波
	    sock=self.server.socket
            self.client.broadcast(sock,target_node_address,msg_bytes)
            
      

    # def store(self, key, value, sock, server_node_id, target_node_address):
    #     payload = packet.Store(key, value, self.node_id, server_node_id)
    #     msg_obj = packet.Message("store", payload)
    #     msg_bytes = pickle.dumps(msg_obj)
    #     self.client.store(sock, target_node_address, msg_bytes)
    def simubroad(self,message):
        print("enter simu")
	#message放入端口中储存
	self.server.node_manager.tablsp.addmessage(message)
        self.asklsp()#发送收集请求
        
    def asklsp(self,address=[]):#address代表广播的源地址
	#print "enter asklsp"
        if not address:#如果是广播发起节点
            payload=packet.askinf(self.tablsp.basetable[0],
                                       self.tablsp.basetable[1])
            msg_obj=packet.Message("lspr",payload)
            msg_bytes=pickle.dumps(msg_obj)
        if address:#如果是中转节点
            payload=packet.askinf(address[0],address[1])
            msg_obj=packet.Message("lspr",payload)
            msg_bytes=pickle.dumps(msg_obj)
        for x in range(0,self.tablsp.length()):#向LSP中的每个邻居发送请求命令
	    target_node_address=(self.tablsp.neighbourip[x],
	                           self.tablsp.neighbourport[x])
            self.client.asklsp(self.server.socket,target_node_address,msg_bytes)



    def bootstrap(self, seed_nodes=[]):
        """
        根据初始节点引导初始化
        :param seed_nodes:<Node list> 种子节点列表
        :return:
        """
	
        for seed_node in seed_nodes:
	    #判断是否已经存在在邻居中
	   
	    flag=self.tablsp.judnei(seed_node)#不同的格式怎么处理todo
	    print(self.tablsp.basetable[1])
	    if flag==0 :#不在邻居中
            #将该节点放入邻居中
	    	self.tablsp.neighbourip.append(seed_node.ip)
	    	self.tablsp.neighbourport.append(seed_node.port)
	    #设置距离
	   	d=random.choice((1,2,3,4,40,40,40,40))
		print("insert distance in bootrs")
		print(d)
	    	self.tablsp.neighbourdistance.append(d)
            # 握手,加入lsptab中
            	self.sendversion(seed_node,
                              Version(1, int(time.time()), self.node_id, seed_node.node_id,
                                     db.get_block_height(self.blockchain.get_wallet_address()),d))
	#建立邻居完毕后整理lsp
	self.tablsp.generatelsp()
	print("neighbour")
	print(self.tablsp.lsp)
	   

        # for seed_node in seed_nodes:
        #     self.iterative_find_nodes(self.client.node_id, seed_node)

        # if len(seed_nodes) == 0:
        #     for seed_node in self.buckets.get_all_nodes():
        #         self.iterative_find_nodes(self.client.node_id, seed_node)

    def __hash_function(self, key):
        return int(hashlib.md5(key.encode('ascii')).hexdigest(), 16)

    def __get_rpc_id(self):
        return random.getrandbits(constant.BITS)

    def __random_id(self):
        return random.randint(0, (2 ** constant.BITS) - 1)

    # def hearbeat(self, node, bucket, node_idx):
    #     # buckets在15分钟内节点未改变过需要进行refresh操作（对buckets中的每个节点发起find node操作）
    #     # 如果所有节点都有返回响应，则该buckets不需要经常更新
    #     # 如果有节点没有返回响应，则该buckets需要定期更新保证buckets的完整性
    #     node_id = node.node_id
    #     ip = node.ip
    #     port = node.port

    #     tm = int(time.time())
    #     if tm - int(self.alive_nodes[node_id]) > 1800:
    #         # 节点的更新时间超过1min，认为已下线，移除该节点
    #         bucket.pop(node_idx)
    #         self.alive_nodes.pop(node_id)

    #     # print '[Info] heartbeat....'
    #     self.ping(self.server.socket, node_id, (ip, port))

    def minner(self):
        while True:
            # blockchain多个线程共享使用，需要加锁
            time.sleep(10)

            try:
                with self.lock:
                    new_block = self.blockchain.do_mine()
                # 广播区块
                # TODO 检测包大小，太大会导致发送失败
                self.sendblock(new_block)
            except Error as e:
                pass

            self.blockchain.set_consensus_chain()  # pow机制保证最长辆（nonce之和最大的链）

    # def set_data(self, key, value):
    #     """
    #     数据存放:
    #     1.首先发起节点定位K个距离key最近的节点
    #     2.发起节点对这K个节点发送STORE消息
    #     3.收到STORE消息的K个节点保存(key, value)数据

    #     :param key:
    #     :param value:
    #     :return:
    #     """
    #     data_key = self.__hash_function(key)
    #     k_nearest_ndoes = self.iterative_find_nodes(data_key)
    #     if not k_nearest_ndoes:
    #         self.data[str(data_key)] = value
    #     for node in k_nearest_ndoes:
    #         self.store(data_key, value, self.server.socket, node.node_id, (node.ip, node.port))

    # def get_data(self, key):
    #     """
    #     读取数据
    #     1.当前节点收到查询数据的请求(获取key对应的value)
    #     2.当前节点首先检测自己是否保存了该数据，如果有则返回key对应的value
    #     3.如果当前节点没有保存该数据，则计算获取距离key值最近的K个节点，分别向这K个节点发送FIND VALUE的操作进行查询
    #     4.收到FIND VALUE请求操作的节点也进行上述(2)~(3)的过程（递归处理）
    #     :param key:
    #     :param value:
    #     :return:
    #     """
    #     data_key = self.__hash_function(key)
    #     if str(data_key) in self.data:
    #         return self.data[str(data_key)]
    #     value = self.iterative_find_value(data_key)
    #     if value:
    #         return value
    #     else:
    #         raise KeyError

    def sendtx(self, tx):
        """
        广播一個交易
        :param tx:
        :return:
        """
        #向tablsp中的所有节点广播
        data_key = self.__hash_function(tx.txid)
        k=self.tablsp.length()
        # k_nearest_ndoes = self.iterative_find_nodes(data_key)
        # if not k_nearest_ndoes:
        #     self.data[data_key] = tx
	print("sa")
	print(self.tablsp.neighbourip)
	print(self.tablsp.neighbourport)
        print(k)
	
        for x in range(k):
            tx.from_id = self.node_id
	    ip=self.tablsp.neighbourip[x]
	    port=self.tablsp.neighbourport[x]
            msg_obj = packet.Message("sendtx", tx)
            msg_bytes = pickle.dumps(msg_obj)
            self.client.sendtx(self.server.socket, (ip, port), msg_bytes)

    # def sendblock(self, block):
    #     """
    #     广播一个block
    #     :param block:
    #     :return:
    #     """
    #     #同理
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

    def sendversion(self, node, version):
        msg_obj = packet.Message("version", version)
        msg_bytes = pickle.dumps(msg_obj)
        self.client.sendversion(self.server.socket, (node.ip, node.port), msg_bytes)

    # def sendverck(self, node, verack):
    #     msg_obj = packet.Message("verack", verack)
    #     msg_bytes = pickle.dumps(msg_obj)
    #     self.client.sendverack(self.server.socket, (node.ip, node.port), msg_bytes)

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
