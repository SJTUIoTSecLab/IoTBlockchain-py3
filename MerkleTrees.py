# coding:utf-8
import hashlib
from collections import OrderedDict

from transaction import Transaction, Tx_vid, Tx_report


class MerkleTrees(object):
    def __init__(self, transaction_list=None):
        self.transaction_list = transaction_list
        self.transactions = transaction_list
        self.transaction_tree = OrderedDict()
        self.create_tree()

    def create_tree(self):
        transaction_list = self.transaction_list
        transaction_tree = self.transaction_tree
        temp_transaction = []
        if len(transaction_list) == 0:
            return
        if len(transaction_list) != 1:
            # print transaction_list

            for index in range(0, len(transaction_list), 2):
                left_leaf = transaction_list[index]

                if index + 1 != len(transaction_list):
                    right_leaf = transaction_list[index + 1]
                else:
                    right_leaf = transaction_list[index]

                if isinstance(left_leaf, Transaction) or isinstance(left_leaf, Tx_vid) or isinstance(left_leaf, Tx_report):
                    left_leaf = left_leaf.txid
                if isinstance(right_leaf, Transaction) or isinstance(right_leaf, Tx_vid) or isinstance(right_leaf, Tx_report):
                    right_leaf = right_leaf.txid

                left_leaf_hash = hashlib.sha256(left_leaf.encode("utf8")).hexdigest()  # 左边叶子节点的哈希值
                right_leaf_hash = hashlib.sha256(right_leaf.encode("utf8")).hexdigest()  # 右边叶子节点的哈希值

                transaction_tree[left_leaf] = left_leaf_hash
                transaction_tree[right_leaf] = right_leaf_hash

                temp_transaction.append(left_leaf_hash + right_leaf_hash)

            self.transaction_list = temp_transaction
            self.transaction_tree = transaction_tree
            self.create_tree()
        else:
            root_leaf = transaction_list[0]
            if isinstance(root_leaf, Transaction) or isinstance(root_leaf, Tx_vid) or isinstance(root_leaf, Tx_report):
                root_leaf = root_leaf.txid
            else:
                root_leaf = root_leaf

            root_leaf_hash = hashlib.sha256(root_leaf.encode("utf8")).hexdigest()
            transaction_tree[root_leaf] = root_leaf_hash
            self.transaction_tree = transaction_tree

    def get_transaction_tree(self):
        return self.transaction_tree

    def get_transaction_list(self):
        return self.transactions

    def get_root_leaf(self):
        # print self.transaction_tree.keys()
        assert len(self.transaction_tree.keys()) > 0
        last_key = list(self.transaction_tree.keys())[-1]
        return self.transaction_tree[last_key]
