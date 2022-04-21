# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 13:45:27 2021

@author: roozbeh
"""

"""create CryptoCurrency ! """

import datetime
import hashlib
import json
from flask import Flask,jsonify,request
import requests
from uuid import uuid4
from urllib.parse import urlparse



#part 1 - building a blockchain
class Blockchain:
    def __init__(self):
        self.chain=[]
        self.transactions=[]
        self.create_block(proof=1,pervious_hash='0')
        self.nodes=set()
        
    def create_block(self,proof,pervious_hash):
        block={
            'index':len(self.chain)+1,
            'timestamp':str(datetime.datetime.now()),
            'proof':proof,
            'transactions':self.transactions,
            'pervious_hash':pervious_hash
            }
        self.transactions = []

        self.chain.append(block)
        return block
    
    def add_transaction(self,sender,reciever,amount):
        self.transactions.append({
            'sender':sender,
            'reciever':reciever,
            'amount':amount
            })
        pervious_block = self.get_pervious_block()
        return pervious_block['index']+1
        
    def add_node(self,address):
        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            
            if response.status_code == 200:
                length = response.json()['len']
                chain = response.json()['chain']
                
                if length > max_length and self.is_chain_valid(chain):
                    longest_chain = chain
                    max_length = length
                    
        if longest_chain:
            self.chain = longest_chain
            return True
            
        return False
    
    
    def get_pervious_block(self):
        return self.chain[-1]
    
    def proof_of_work(self,pervious_proof):
        new_proof=1
        check_proof=False
        while check_proof is False:
            hash=hashlib.sha256(str(new_proof**2 - pervious_proof **2).encode()).hexdigest()
            if hash[:4] == '0000':
                check_proof= True
            else:
                new_proof+=1
            
        return new_proof
    
    def hash(self,block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self,chain):
        pervious_block=chain[0]
        block_index=1
        while block_index < len(chain):
            block = chain[block_index]
            if block['pervious_hash'] != self.hash(pervious_block):
                return False
            pervious_proof = pervious_block['proof']
            proof = block['proof']
            hash=hashlib.sha256(str(proof**2 - pervious_proof **2).encode()).hexdigest()
            if hash[:4] != '0000':
                return False
            pervious_block = block
            block_index +=1
            
        return True

#creating web app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False



#creating address for the node on port 5000
node_address = str(uuid4()).replace('-', '')

#creating blockchain
blockchain= Blockchain()

#part 2 - mining our blockchian

@app.route("/min_blcok",methods=['GET'])
def mine_block():
    pervious_block= blockchain.get_pervious_block()
    pervious_proof = pervious_block['proof']
    proof= blockchain.proof_of_work(pervious_proof)
    pervious_hash = blockchain.hash(pervious_block)
    blockchain.add_transaction(node_address, 'secend', 1)
    newblock= blockchain.create_block(proof, pervious_hash)
    response={
        'message':'good good you mined a block !!',
        'block':newblock
        }
    return jsonify(response), 200
@app.route("/get_chain",methods=['GET'])
def get_chain():

    response={
        'chain':blockchain.chain,
        'len':len(blockchain.chain)
        }
    return jsonify(response), 200

#is chain valid 
@app.route("/is_valid",methods=['GET'])
def is_valid():
    is_chain_valid = blockchain.is_chain_valid()
    if is_chain_valid:
        response={
            'message':'good good the chain is valid',
            'chain':blockchain.chain
            }
    else:
        response={
            'message':'bad bad somthing is wrong in your chain',
            'chain':blockchain.chain
            }

    return jsonify(response), 200
#Add new transaction

@app.route("/add_transaction",methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','reciever','amount']
    if not all(key in json for key in transaction_keys):
        return 'some element of transaction are missing ',400
    index = blockchain.add_transaction(json['sender'], json['reciever'], json['amount'])


    response={
        'message':f'good good your transaction save in Block number {index} !!',

        }
    return jsonify(response), 201

#part 3 - decentrelize out block chain


#connecting new nodes
@app.route("/connect_node",methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'some element of nodes are missing ',400
    
    for node in nodes:
        blockchain.add_node(node)
        


    response={
        'message':'good good your all nodes is connected now!!',
        'total_nodes': list(blockchain.nodes)

        }
    return jsonify(response), 201

#replace the chain with the largest chain
@app.route("/replace_chain",methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response={
            'message':'the chain replaced with the largest chain',
            'chain':blockchain.chain
            }
    else:
        response={
            'message':'evry thing is ok your chain is the largest',
            'chain':blockchain.chain
            }

    return jsonify(response), 200

#running the app
app.run(host='0.0.0.0',port=5002)










