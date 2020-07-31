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

### Step 3: Check Simple Information

Open your browser and you can visit the following address to :

- http://127.0.0.1:5001/height : get the height of blockchain

- http://127.0.0.1:5001/tx_in_block?block_index=1 : get the information of transactions in a certain block

	e.g.

	```
	{"0": {"txid": "c8a8019259f6779b274206e8a9da0c7821003009165a48eb2d60bec7807ad09b", "timestamp": "2020-07-31 20:53:36", "type": "vid", "vid": "a3.0"}, "1": {"txid": "8d9a1dada6191edd5f5d379274e0dba4432206da86dfd227bebb20eb7f10dda0", "timestamp": "2020-07-31 20:53:43", "type": "report", "edgeId": "m1", "meanSpeed": 20.844183340424205, "vehicleNum": 2}}
	```


Or send a post request to the following address to :

- http://127.0.0.1:5000/transactions/new : create a new transaction

## Packaged App (Executable Files)

Executable files have been packaged in ```/dist``` (https://github.com/SJTUIoTSecLab/IoTBlockchain) . Start the nodes and simulate trading simply by execute :

```shell
run -p 5000
run -p 5001
run -p 5002

simulation_test
```

## About the broadcast network

Run and test the part of broadcast network separately.  

**Step 1 :** Start 10 nodes (port 5000 - 5009). The code to execute is almost the same as above.

**Step 2 :** Construct the broadcast network by executing ```python broadcast_test.py```.