# 5G-VN Blockchain

## Introduction

This is a block chain demo for 5G-Vehicular networking, which adopts self-designed consensus protocol and distribution network to meet the two characteristics of high reliability and low lantency time.

## Getting Started

### Step 1 : Start Nodes

Execute the following command to start some nodes :

```shell
python run.py -p 5000 &
python run.py -p 5001 &
python run.py -p 5002 &
```

### Step 2 : Simulate Transactions

Run ```simulation.py``` (need [SUMO](https://www.eclipse.org/sumo/) installed and configured):

```shell
python simulation.py
```

Transactions (Internet of Vehicles) is simulated.

Run ```simulation_easy_test.py``` instead if you have not get SUMO installed yet. It provides simulation of easy and rough transactions. 

File ```simulation_test.py``` provides a better simulation of  transactions, which includes functions of UTXO, signature, etc. (Bug unfixed)

### Step 3: Check Simple Information

Open your browser and you can visit the following address to :

- http://127.0.0.1:5001/height : get the height of blockchain

- http://127.0.0.1:5001/GST : get GST

- http://127.0.0.1:5001/step : get time step of the views

- http://127.0.0.1:5002/block_info?block_index=1 : get the information of a certain block

	e.g.

	```
	{"current_hash":"da8865d58a3ba72618de506a6a768a4001369ed95843d340e421dd41e3883998","index":1,"merkleroot":"a2390105c10af9526b19687aeca73e22484a728f67c08c1c66a69ca79afdc414","previous_hash":"000059507af592941b360c6f5b8d3514ebc76045c48eef3505ea101bcef7c5f6","transactions":[{"timestamp":1598184686,"txid":"b4c311195ef8b0a61620f9e76c25af7a468526c8f586dd3f73cd9d6dbc871c37","type":"vid","vid":"a3.0"},{"edgeId":"m1","meanSpeed":20.844183340424205,"timestamp":1598184694,"txid":"2bf61ab1f815013e567aa067602df12ce1edd71db169f30dc0f5a3adc2dfd8a6","type":"report","vehicleNum":2}],"view":1}
	```

- http://127.0.0.1:5002/tx_in_block?block_index=1 : get the information of transactions in a certain block

  e.g.

  ```
  {"0": {"txid": "c8a8019259f6779b274206e8a9da0c7821003009165a48eb2d60bec7807ad09b", "timestamp": "2020-07-31 20:53:36", "type": "vid", "vid": "a3.0"}, "1": {"txid": "8d9a1dada6191edd5f5d379274e0dba4432206da86dfd227bebb20eb7f10dda0", "timestamp": "2020-07-31 20:53:43", "type": "report", "edgeId": "m1", "meanSpeed": 20.844183340424205, "vehicleNum": 2}}
  ```

- http://127.0.0.1:5002/asyn_node?view=1 : get the rate of asynchronous nodes of a certain view

- http://127.0.0.1:5002/asyn_node_all : get the rate of asynchronous nodes of all views

- http://127.0.0.1:5000/consensus_time?view=1 : get the time for consensus of a certain view (main node only so far)

- http://127.0.0.1:5000/consensus_time_all : get the time for consensus of all views (main node only so far)

- http://127.0.0.1:5002/block_time : get real time of all views (close to ```step``` of course)

- http://127.0.0.1:5002/get_block_time?view=2 : get real time of a certain view (close to ```step``` of course)

Or send a post request to the following address to :

- http://127.0.0.1:5000/transactions/new : create a new transaction
- http://127.0.0.1:5000/transactions/new_easy : create a new easy transaction
- http://127.0.0.1:5000/transactions/new_vid or http://127.0.0.1:5000/transactions/new_report for other type of transactions (Internet of Vehicles, SUMO)

## Notes

### 重要参数设置

- 时间窗口初始值 : ```p2p > node.py > NodeManager > _init_ > self.GST = 5```
- 每轮共识开始时间间隔 : ```p2p > node.py > NodeManager > _init_ > self.step = 10```

