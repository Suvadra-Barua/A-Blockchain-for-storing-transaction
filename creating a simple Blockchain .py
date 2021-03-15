import datetime
import hashlib
import json
from flask import Flask, jsonify, request

# Part 1 - Building a Blockchain

class Blockchain():
    def __init__(self):
        self.users_list=[]
        self.transactions_list=[]
        self.chain=[]
        #self.create_block(proof=1,previous_hash='0')
        
    
    def register_user(self,name):
        user={'ID':len(self.users_list)+1,
              'Name':name,
              'Coin':'100'
                }
        self.users_list.append(user)
        return user
    
    def mine_coin(self,user_id,coin):
        user=self.users_list[user_id-1]
        user['Coin']=str(int(user['Coin'])+int(coin))
        return True
    
    def transection(self,sender_id,coin,receiver_id):
        sender=self.users_list[sender_id-1]
        receiver=self.users_list[receiver_id-1]
        if int(sender['Coin'])>=int(coin):
            sender['Coin']=str(int(sender['Coin'])-int(coin))
            receiver['Coin']=str(int(receiver['Coin'])+int(coin))
            message={'Message':sender['Name']+" send "+coin+" Coin to "+receiver['Name'],
                     'Time':str(datetime.datetime.now())}
            self.transactions_list.append(message)
            return True
        else:
            return False
        
    def del_transaction(self):
        del self.transactions_list[0:5]
        
        
    def create_block(self,proof,previous_hash):
        #t=self.transactions_list
        block={'Index': len(self.chain)+1,
               'Timestamp': str(datetime.datetime.now()),
               'Proof':proof,
               'Transaction':self.transactions_list[0:5],
               'Previous_Hash':previous_hash}
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self,previous_proof):
        new_proof=1
        check_proof=False
        while check_proof is False:
            hash_operation=hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]=='0000':
                check_proof=True
            else:
                new_proof+=1
        return new_proof
    
    def hash_block(self,block):
        encoded_block=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def chain_is_valid(self):
        previous_block=self.chain[0]
        block_index=1
        while block_index<len(self.chain):
            block=self.chain[block_index]
            if block['Previous_Hash']!=self.hash_block(previous_block):
                return False
            previous_proof=previous_block['Proof']
            proof=block['Proof']
            hash_operation=hashlib.sha256(str(proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]!='0000':
                return False
            previous_block=block
            block_index+=1
        return True
   
#part2-mining a new block

app=Flask(__name__)

blockchain=Blockchain()


@app.route('/Register_user/<name>', methods = ['GET'])
def Register_user(name):
    user=blockchain.register_user(name)
    response={'ID':user['ID'],
              'Name':user['Name'],
              'Coin':'100'
                }
    return jsonify(response), 200
        
@app.route('/users', methods = ['GET'])
def users():
    response = {'Users': blockchain.users_list,
                'length': len(blockchain.users_list)}
    return jsonify(response), 200   
#@app.route('/mine_block',methods=['GET'])

def mine_block():
    previous_block=blockchain.get_previous_block()
    previous_proof=previous_block['Proof']
    proof=blockchain.proof_of_work(previous_proof)
    previous_hash=blockchain.hash_block(previous_block)
    block=blockchain.create_block(proof,previous_hash)
    response={'message': 'Congratulations, Transactions successfully have been stored!',
                'Index': block['Index'],
                'Timestamp': block['Timestamp'],
                'Proof': block['Proof'],
                'Transactions':block['Transaction'],
                'Previous_Hash': block['Previous_Hash']}
    return response

@app.route('/get_chain', methods = ['GET','POST'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200         

@app.route('/is_valid',methods=['GET'])
def is_valid():
    if(blockchain.chain_is_valid() is True):
        response={'messeage':'The Whole Chain is Valid'}
    else:
        response={'messeage':'The Chain is not Valid'}
    return jsonify(response),200

@app.route('/Transaction/<int:sender_id>/<coin>/<int:receiver_id>',methods=['GET','POST'])
def Transaction(sender_id,coin,receiver_id):
    transaction=blockchain.transection(sender_id,coin,receiver_id)
    if(transaction is True and len(blockchain.transactions_list)==5 and len(blockchain.chain)==0):
        block=blockchain.create_block(1,'0')
        response={'message': 'Congratulations, Transactions successfully have been stored!',
                'Index': block['Index'],
                'Timestamp': block['Timestamp'],
                'Proof': block['Proof'],
                'Transactions':block['Transaction'],
                'Previous_Hash': block['Previous_Hash']}
        blockchain.del_transaction()
    elif(transaction is True and len(blockchain.transactions_list)==5 and len(blockchain.chain)>0):
        response=mine_block()
        blockchain.del_transaction()
    elif(transaction is True and len(blockchain.transactions_list)!=5):
        response=blockchain.transactions_list[-1]
    else:
        response={'Message':blockchain.users_list[sender_id-1]['Name']+" should mine coin"}
    return jsonify(response),200

@app.route('/mineCoin/<int:id>/<coin>',methods=['GET'])
def mineCoin(id,coin):
    user =blockchain.users_list[id-1]
    if int(user['Coin'])<20:
        blockchain.mine_coin(id,coin);
        response={'Message': user['Name']+" just mined "+ coin}
    else:
        response={'Message': user['Name']+", You have enough coin for transaction"}
    return jsonify(response),200    
#if __name__=='__main__':
app.run(host='0.0.0.0', port=5000)