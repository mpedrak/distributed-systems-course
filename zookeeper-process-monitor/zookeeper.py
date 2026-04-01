# Imports

import subprocess
import logging
import sys
import os

from kazoo import client
from kazoo.client import KazooClient, KazooState
from kazoo.protocol.states import EventType

# Inicialization

if len(sys.argv) != 4:
    print("Wrong argument count, must be three - znode name, ip:port and path to program.")
    exit(0)

znode_name, ip_port, program_path  = sys.argv[1], sys.argv[2], sys.argv[3]

if not os.path.isfile(program_path):
    print("Wrong path to program.")
    exit(0)

def my_listener(state):
    if state == KazooState.LOST: print("\rSession lost.")
    elif state == KazooState.SUSPENDED: print("\rDisconnected from Zookeeper.")
    else: print("\rConnected to Zookeeper.")

program_process = None
watched_children = set()
logging.basicConfig()
zk = KazooClient(hosts = ip_port)
zk.add_listener(my_listener)
zk.start()

# Watching functions

def get_child_count(zk, path):
    children_list = zk.get_children(path)
    sum = len(children_list)
    for x in children_list: sum += get_child_count(zk, path + "/" + x)
    return sum

def update_watched_children_set(zk, path = None):
    global watched_children
    if path is None:
        watched_children = set()
        path = znode_name
        watched_children.add(path)
        
    children_list = zk.get_children(path)
    for x in children_list: 
        child_path = path + "/" + x
        if child_path not in watched_children:
            watched_children.add(child_path)
            update_watched_children_set(zk, child_path)

def children_znode_watch(children_list, event):
    if event is None:
        return 
    for x in children_list:
        child_path = event.path + "/" + x
        if child_path not in watched_children:
            zk.ChildrenWatch(path = child_path, func = children_znode_watch, send_event = True)
            watched_children.add(child_path)

    update_watched_children_set(zk) 
    print(f"\rRoot znode {znode_name} has {get_child_count(zk, znode_name)} childs.")

def initial_children_znode_watch(zk, path):
    zk.ChildrenWatch(path = path, func = children_znode_watch, send_event = True)
    watched_children.add(path)
    children_list = zk.get_children(path)
    for x in children_list:
        child_path = path + "/" + x
        if child_path not in watched_children: initial_children_znode_watch(zk, child_path)
            
@client.DataWatch(zk, znode_name)
def root_znode_watch(data, stat, event):
    global program_process, watched_children
    if event is None: 
        return
    elif event.type == EventType.CREATED:
        print(f"\rCreated root znode and started running given program.")     
        if program_process is None: program_process = subprocess.Popen(program_path)
        zk.ChildrenWatch(path = znode_name, func = children_znode_watch, send_event = True)
    elif event.type == EventType.DELETED:
        print(f"\rDeleted root znode and stopped given program.")
        watched_children = set()
        if program_process is not None: 
            program_process.terminate()
            program_process = None

# Printing tree        

def print_tree(current_path = None, children_list = None, level = 0):  
    if current_path is None:
        if not zk.exists(znode_name):
            print("Tree is empty.")
            return

        print(znode_name)
        children_list = zk.get_children(znode_name)
        for x in children_list:
            path = znode_name + "/" + x
            print("└-/" + x)
            result = zk.get_children(path)
            print_tree(path, result, level + 1)
    else:
        for x in children_list:
            path = current_path + "/" + x
            print("   " * level, end = "")
            print("└-/" + x)
            result = zk.get_children(path)
            print_tree(path, result, level + 1);  

# Start waiting

if zk.exists(znode_name): 
    watched_children = set()
    print("Root znode exists, so given program started running.")     
    program_process = subprocess.Popen(program_path)
    initial_children_znode_watch(zk, znode_name)

print(f"Watching started, znode name of root : {znode_name}, to print structure of tree - tree, to end - exit.")

while True:
    try: line = input("> ")
    except: break

    if line is None: continue
    elif line == "exit": break
    elif line == "tree": print_tree()
    else: print("Wrong command.")

zk.stop()
if program_process is not None: program_process.terminate()
