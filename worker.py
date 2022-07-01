'''
Purpose:    A01 - Workers for the 2PC
Author:     Byaruhanga Asiimwe Sami
Student #:  007793446
Email:      byaruhaa@myumanitoba.ca
Submission: T/May/24th/2022
Resources:  test_cli.py, test_worker.py provided by prof
'''

import socket
import sys
import json
import time 
import select
import random
'''************** STEPS TO COMPLETE WORKER: ************************
functions: set up useful functions
initialization: aka getting port info
connection + processing:
    connection: listening for coordinator
    Processing: sending to coordinator
****************************************************************'''


#INTIALIZATION ----------------------------------------------------
print('Running worker ... ')
myDB = {'name':'Sami', 'course':'3010', 'P':'=NP'}

if len(sys.argv)!=2: #sys.argv - An array cmd i/p
    print('Please specify the workers port #')
    sys.exit(1)

serverHost = ''
serverPort = int(sys.argv[1])
print('Connecting to '+ sys.argv[1]) #prints val on index 1 of arry
#-------------------------------------------------------------------



#FUNCTIONS ---------------------------------------------------------
#NOTE=>: they are short so just put these in my running program
def get(key):
    '''
    GET: Fetches a val for a key
    RQST: {"type": "GET", "key": key} 
    RETURNS: 
        Not there = {"type": "GET-RESPONSE", "key": "P", "value": None} 
        Exists = {"type": "GET-RESPONSE", "key": "P", "value": "The value"}
    '''
    result = {}
    if(key in myDB.keys()): #Val exists
        result = {"type": "GET-RESPONSE", "key": key, "value": myDB.get(key)}
        # print(returnGet2)
    else: #val does not exist
        result = {"type": "GET-RESPONSE", "key": key, "value": None}
        # print(returnGet)
    return result

def commit(key, val):
    '''
    COMMIT: the changes to the worker
    RQST: {"type": "COMMIT", "key": key, "value": value} 
    RESPONSE:
        {type: "COMMIT-REPY", "key":"k", "value":true}
    '''
    myDB[key] = val
    result = {"type": "COMMIT-REPLY", "key":key, "value":val}
    # try: #commit went smooth
    #     # print("OLD DB: >", myDB)
    #     myDB.update({key:val})
    #     # print("NEW DB: >", myDB)
    #     result = {"type": "COMMIT-REPLY", "key":key, "value":True}
    # except Exception as e: #commit not smooth: not doing much
    #     print(e)
    #     result = {"type": "COMMIT-REPY", "key":key, "value":False}
    return result
#-------------------------------------------------------------------



#Connection + Processing--------------------------------------------
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((serverHost,serverPort)) 
serverSocket.listen()
myReadables = [serverSocket, ]
myWriteables = []
myClients = []

##Will be used for setting the lock
isLocked = False
lockSeconds = 2 #To see lock coming in use this!
# lockSeconds = (random.random()/8 + 0.01)
keyLockList = []

##Will be used as timer
startTime = time.time()
stopTime = startTime + lockSeconds
napTime = time.sleep(random.random()/8 + 0.01)
while True:
    try:
        readable, writeable, exceptions = select.select(
            myReadables + myClients, myWriteables, myReadables, 5
        ) 
         
        # print('released from block')
        for skt in readable:
            if skt is serverSocket: #new client
                conn, addr = serverSocket.accept()
                print('Adding client =>', addr)
                myClients.append(conn)
            elif skt in myClients: #already exists then read
                data = skt.recv(1024)
                strData = data.decode('UTF-8')

                if data: #check if we have something
                    jData = json.loads(strData)
                    type = jData['type']
                    key = jData['key']

                    if type == 'GET':
                        print('\nGot Request for key=>', key)
                        result = get(key)
                        # print('results from function is -> ', result)
                        napTime ##WAIT
                        conn.sendall(json.dumps(result).encode())
                        print('Finished processing GET request\n')
                
                    if type == 'QUERY':
                        print('\nGot Query for key=>',key)
                        val = jData['value']
                        '''
                        
                        #This is prints for debugging
                        print('KeyLockList =>',keyLockList)
                        print('Lock state -=>', isLocked)
                        print('Start time -=>', startTime)
                        print('StopTime ---=>', stopTime)
                        print('lockseconds =>', stopTime-startTime)
                        print('time.time --=>', time.time())
                        print('time.time - stoptime (timeleft) =>', time.time()-stopTime)
                        # '''
                        if key in keyLockList: #Key is in my keylocklist
                            # print('\nKey is in in keyLockList')
                            isLocked = False
                            reply = {"type": "QUERY-REPLY", "key": key, "answer":isLocked}
                            napTime
                            conn.sendall(json.dumps(reply).encode())
                        else: #Key is not in my keyList
                            print('\nKey not in keyList')
                            keyLockList.append(key)
                            isLocked = True
                            reply = {"type": "QUERY-REPLY", "key": key, "answer":isLocked}
                            napTime
                            conn.sendall(json.dumps(reply).encode())
                            # print('Timeout set for =>', lockSeconds)
                        if (time.time()-stopTime) >= lockSeconds: #Timeout so i reset all
                            # print('just exited timeout')
                            keyLockList.remove(key)
                            startTime = time.time()
                            stopTime = startTime + lockSeconds
                            isLocked = False
                        time.sleep(random.random()/8 + 0.01)
                        print('Finished processing get QUERY\n')
    
                    if type == 'COMMIT':
                        val = jData['value']
                        print('\nGot Commit for Key=>',key,' with value=>', val)
                        result = commit(key, val)
                        conn.sendall(json.dumps(result).encode())
                        napTime
                        print('Finished processing COMMIt\n')

                    clean = strData.strip()
                    if clean=='' or clean == 'exit':
                        skt.close()
                        myClients.remove(skt)
                else:
                    print('Removing Coordinator')
                    myClients.remove(skt)
            for problem in exceptions:
                print("Exception occured")
                if problem in myClients:
                    myClients.remove(problem)
        
    except KeyboardInterrupt as e:
        print('Keyboard interrupt')
        sys.exit(0)
    except socket.timeout as e:
        print('timeout occured')
    except Exception as e:
        print('This exception occured =>',e)
        sys.exit(0)
#------------------------------------------------------------------

# ****************** PROGRAM ENDS HERE ****************************