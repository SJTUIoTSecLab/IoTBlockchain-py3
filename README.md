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

### Step 2 : Simulate Trading

Run ```simulation_test.py``` ：

```shell
python simulation_test.py
```

### Step 3: Check Simple Information

Open your browser and you can visit the following address to :

- http://127.0.0.1:5001/height ：get the height of blockchain
- http://127.0.0.1:5001/block_info?height=1 ：get the information of certain block

Or send a post request to the following address to:

- http://127.0.0.1:5000/transactions/new ：create a new transaction

## Packaged App (Executable Files)

Executable files have been packaged in ```/dist```. Start the nodes and simulate trading simply by execute :

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