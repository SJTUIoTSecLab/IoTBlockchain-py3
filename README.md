# 5G-VN Blockchain

## Introduction

This is a block chain demo for 5G-Vehicular networking, which adopts self-designed consensus protocol and distribution network to meet the two characteristics of high reliability and low lantency time.

## Getting Started

### Step 1 : Start Nodes

Execute the following command to start some nodes.

```powershell
# Server node
python deploy.py -s

# Other nodes
python deploy.py
```

### Step 2 : Simulate Transactions

Will be automatically performed.

---

Run `simulation.py` (need [SUMO](https://www.eclipse.org/sumo/) installed and configured) :

```shell
python simulation.py
```

Transactions (Internet of Vehicles) is simulated.

Run `simulation_easy_test.py` instead if you have not get SUMO installed yet. It provides simulation of easy and rough transactions. 

File `simulation_test.py` provides a better simulation of  transactions, which includes functions of UTXO, signature, etc. (Bug unfixed)

### Step 3: Check Simple Information

Open your browser and you can visit the following address to :

- http://127.0.0.1:30134/height : get the height of blockchain

- http://127.0.0.1:30134/GST : get GST

- http://127.0.0.1:30134/step : get time step of the views

- http://127.0.0.1:30134/block_info?block_index=1 : get the information of a certain block

	```
	{"current_hash":"2afad5781174e4db6e92927eadbb91372c949e074ab7b19daa78e16410c12795","index":1,"merkleroot":"608f06bbada61daa5f52c8a529b98b51d8ba119e1ea171430864e9b55e4fc983","previous_hash":"a374ecae0a18b7ae126deb10b08773aa482348db60048f5193a4c4612f247344","timestamp":1598500523,"transactions":[{"timestamp":1598500523,"txid":"bdb613fe08a6a6b904992d00b525f3e64de9e97da36de3664c41c0fd87f68a83","type":"vid","vid":"a3.0"},{"edgeId":"m1","meanSpeed":20.844,"timestamp":1598500530,"txid":"a4a6a5c30d15b691884125f119fa6c4e2a9d16f19747578f3a3fb7638452776d","type":"report","vehicleNum":2}]}
	```

- http://127.0.0.1:30134/tx_in_block?block_index=1 : get the information of transactions in a certain block

	```
	{"0": {"txid": "c8a8019259f6779b274206e8a9da0c7821003009165a48eb2d60bec7807ad09b", "timestamp": "2020-07-31 20:53:36", "type": "vid", "vid": "a3.0"}, "1": {"txid": "8d9a1dada6191edd5f5d379274e0dba4432206da86dfd227bebb20eb7f10dda0", "timestamp": "2020-07-31 20:53:43", "type": "report", "edgeId": "m1", "meanSpeed": 20.844, "vehicleNum": 2}}
	```

- http://127.0.0.1:30134/asyn_node?view=1 : get the rate of asynchronous nodes of a certain view

- http://127.0.0.1:30134/asyn_node_all : get the rate of asynchronous nodes of all views

- http://127.0.0.1:30134/consensus_time?view=1 : get the time for consensus of a certain view (main node only so far)

	```
	{"time":[0.074,6.088],"view":1}
	```

  注：收集完交易时记录时间，发送新一轮request时记录时间。"time" list 中的第一项是从【交易收集完】到【主节点收到法定个数个reply，共识达成】的时间；第二项是从【主节点send request，发起新一轮共识】到【主节点收到法定个数个reply，共识达成】的时间，包括了收集交易的时间，包含了时间窗口。

- http://127.0.0.1:30134/consensus_time_all : get the time for consensus of all views (main node only so far)

- http://127.0.0.1:30134/block_time : get real time of all views (close to `step` of course)

- http://127.0.0.1:30134/get_block_time?view=2 : get real time of a certain view (close to `step` of course)

Or send a post request to the following address to :

- http://127.0.0.1:30134/transactions/new : create a new transaction

	```
	{
		'amount': 1, 
		'sender': '23DvZ2MzRoGhQk4vSUDcVsvJDEVb', 
		'receiver': '4ZfwxpSCkceptcKH74WrQ3PVASR4'
	}
	```

- http://127.0.0.1:30134/transactions/new_easy : create a new easy transaction (‘amount’, ‘sender’, ‘receiver’, same as the previous one)

- http://127.0.0.1:30134/transactions/new_vid or http://127.0.0.1:30134/transactions/new_report for other type of transactions (Internet of Vehicles, SUMO)

	```
	{
		'vid': 'a3.0'
	}
	```
	
	or
	
	```
	{
		'edgeId': 'm1',
		'meanSpeed': 20.844,
		'vehicleNum': 2
	}
	```

## Notes

### 重要参数设置

- 时间窗口初始值 : `p2p > node.py > NodeManager > _init_ > self.GST = 1`
- 每轮共识开始时间间隔 : `p2p > node.py > NodeManager > _init_ > self.step = 5`

### New Node & Restart

系统运行过程中加入新的共识节点```python deploy.py -c```

节点掉线后再重新启动节点`python deploy.py -r -p $port$`

