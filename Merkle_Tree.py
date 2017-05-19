import hashlib
import binascii
import random
import time
import copy


class MT:

    def __init__(self):
        self.root = None
        self.number_of_nodes = 0
        self.leaves_array = []

    def merkle_tree(self, input_list, hash_algo='sha256'):
        for element in input_list:
            self.add_data_block(element, hash_algo)
        self.root = self.create_tree(hash_algo=hash_algo)

    def add_data_block(self, block_data, hash_algo='sha256'):
        new_node = self.new_node()
        MT.hash(new_node, block_data, hash_algo)
        self.leaves_array.append(new_node)

    def create_tree(self, node_list=None, hash_algo='sha256'):
        if node_list is None:
            node_list = self.leaves_array
        new_node_list = []
        enum = enumerate(node_list)
        for i, node in enum:
            new_node = self.new_node()
            new_node.hash_val = node.hash_val
            new_node.left_child = node
            node.parent = new_node
            if i + 1 < len(node_list):
                i, node = next(enum)
                new_node.hash_val += node.hash_val
                new_node.right_child = node
                node.parent = new_node
            else:
                new_node.hash_val += new_node.hash_val

            MT.hash(new_node, new_node.hash_val, hash_algo)
            new_node_list.append(new_node)
        if len(new_node_list) == 1:
            return new_node_list[0]
        else:
            return self.create_tree(new_node_list, hash_algo)

    def new_node(self):
        new_node = Node()
        self.number_of_nodes += 1
        new_node.number = self.number_of_nodes
        return new_node

    @staticmethod
    def hash(node, data, hash_algo):
        h = hashlib.new(hash_algo)
        h.update(data)
        node.hash_val = binascii.b2a_hex(h.digest())

    @staticmethod
    def find_improper_blocks(first_node, second_node, list):
        if first_node.hash_val != second_node.hash_val:
            if first_node.is_leaf() and second_node.is_leaf():
                list.append(second_node)
            else:
                MT.find_improper_blocks(first_node.left_child, second_node.left_child, list)
                MT.find_improper_blocks(first_node.right_child, second_node.right_child, list)


class Node:

    def __init__(self):
        self.left_child = None
        self.right_child = None
        self.hash_val = None
        self.parent = None
        self.number = -1

    def is_leaf(self):
        if self.left_child is None and self.right_child is None:
            return True
        else:
            return False

# blake2b is only avaliable in python 3.6, if you are running a lower version of python use 'md5' or 'sha256'
def make_merkle_tree(list, hash_algo='blake2b'):
    merkle_tree = MT()
    start = time.time()
    merkle_tree.merkle_tree(list, hash_algo)
    end = time.time()
    print('Merkle Tree \nTime:', end - start, '\nRoot hash value:', merkle_tree.root.hash_val.decode('utf-8'), '\n')
    return merkle_tree


def make_hash_list(list, hash_algo='blake2b'):
    hashlist = MT()
    start = time.time()
    for item in list:
        hashlist.add_data_block(item, hash_algo)
    end = time.time()
    print(end - start, 'time required to build a list', '\n')
    return hashlist.leaves_array


def list_of_file_lines(file):
    input_list = []
    f = open(file, 'rb')
    for line in f:
        input_list.append(line)
    return input_list


# checking it found the right pieces
def check_improper_blocks(list1, list2):
    if len(list1) != len(list2):
        print('something wrong')
    for node in list2:
        if node.number not in list1:
            print(node.number, ' was not expected')

file1 = list_of_file_lines("test.txt")
file2 = copy.deepcopy(file1)
changing_lines = []
for x in range(5):  # changing some lines in second list
    rand1 = random.randint(0, len(file1))
    rand2 = random.randint(0, len(file1))
    file2[rand2] += file1[rand1]
    changing_lines.append(rand2+1)  # keeping track of which lines to check it later

# blake2b is only avaliable in python 3.6, if you are running a lower version of python use
# make_merkle_tree(file1, 'md5') or make_merkle_tree(file1, 'sha256')
tree1 = make_merkle_tree(file1)
tree3 = make_merkle_tree(file2)  # this is with modified data set

# blake2b is only avaliable in python 3.6, if you are running a lower version of python use
# make_hash_list(file1, 'md5') or make_hash_list(file1, 'sha256')
list1 = make_hash_list(file1)
list3 = make_hash_list(file2)  # this is with modified data set

# search for broken pieces
improper_tree_nodes = []
start = time.time()
MT.find_improper_blocks(tree1.root, tree3.root, improper_tree_nodes)
end = time.time()

check_improper_blocks(changing_lines, improper_tree_nodes)
print(end - start, 'time to find broken pieces using merkle tree', '\n')

improper_list_nodes = []
start = time.time()
for node in list3:
    if node.hash_val != list1[node.number-1].hash_val:
        improper_list_nodes.append(node)
end = time.time()

check_improper_blocks(changing_lines, improper_list_nodes)
print(end - start, 'time to find broken pieces using hash list', '\n')
print('done')
