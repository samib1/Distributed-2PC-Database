'''
Purpose:    A01 - Coordinator for the 2PC
Author:     Sami
'''

import socket
import sys
import json
import select
import random


'''****************** STEPS TO COMPLETE COORDINATOR: **************
initialization: aka getting port info
connection + processing:
    connection:
        connecting to workers 
        listening for cli
    Processing:
        sending to workers 
        sending to cli   
****************************************************************'''

#Intialziation + CLISOCKET: WILL CONNECT TO WORKER ------------------
print('Running coordinator ... ')
if len(sys.argv) < 2: #Need atleast 1 workers info to run
    print('For usage, please pass: <Port> <host:Worker_1_Port> ... <host:Worker_n_Port>')
    sys.exit(1)

serverHost = '' #Might ask user for it and then split index 1 and get the vals
serverPort = int(sys.argv[1]) #for clients to connect to
print('Starting server on port =>', serverPort)

cmdWorkerList = sys.argv[2:]
workerSocketList = []
for addy in cmdWorkerList:
    # print(addy)
    parts = addy.split(':')
    host = parts[0]
    port = int(parts[1])
    workerAddy = (host, port)
    # print (workerAddy)
    try:
        workerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        workerSocket.connect(workerAddy)
        workerSocketList.append(workerSocket)
        print('Connection made to worker w/ info =>', workerAddy)
    except Exception as e:
        # '''
        print('Exception Raised =>',e)
        print('Program stopped: try suggested solutions below')        
        print('Solution1: Make sure ur workers are running first then run co-ordinator')
        print('Solution2: try again after Re-Starting worker w/ different ports')
        print('Solution3: Google the exception raised')#'''
        sys.exit(0)
#-------------------------------------------------------------------



#SEVERSOCKET: SIMILAR TO ECHO_SERVER_W_SELECT PROVIDED BY PROF -----
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((serverHost,serverPort)) 
serverSocket.listen()
myReadables = [serverSocket, ]
myWriteables = []
myClients = []

while True:
    try:
        readable, writeable, exceptions = select.select(
            myReadables + myClients, myWriteables, myReadables, 5
        ) ##5 is how long it will take to release from block

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
                        print('\nGot Request for key =>', key)
                        # content = {"type": "GET", "key": key}
                        myDB = {}
                        myDB = strData
                        randomWorker = random.choice(workerSocketList)
                        randomWorker.sendall(myDB.encode())
                        setResponse = randomWorker.recv(1024)
                        conn.sendall(setResponse)
                        print('recieved from Worker =>',setResponse)
                        print('Finished processing GET request\n')

                    if type == 'SET':
                        val = jData['value']
                        print('\nSet Request for key =>',key, 'to value =>',val)
                        ##SEND A QUERY TO MY WORKERS 
                        query = {"type": "QUERY", "key": key, "value": val}
                        queryResponseList = []
                        answerList = []
            
                        for worker in workerSocketList:
                            worker.sendall(json.dumps(query).encode())
                            queryResponse = worker.recv(1024)
                            # print('recieved from server: ', queryResponse)
                            # queryResponseList.append(queryResponse.decode('UFT-8'))
                            if queryResponse: #Check if we have responces
                                print('recieved from server: ', queryResponse)
                                strQueryResponse = queryResponse.decode('UTF-8')
                                jData = json.loads(strQueryResponse)
                                answer = jData['answer']
                                answerList.append(answer)
                            else: #No response
                                setResponse = {"type": "SET-RESPONSE", "success": False}
                            
                        #Processing then send to commit    
                        # print(queryResponseList)
                        # print(answerList)
                        isCommit = False #Will check worker response if its yes then we send tru
                        if False in answerList:
                            print('Not all workers are ready')
                        else:
                            isCommit = True ##Not accounting for No in workers
                            # print('Yep all worker ready to receive')
                            commitConent = {"type": "COMMIT", "key": key, "value": val}
                            # commitResponseList = []
                            for worker in workerSocketList:
                                worker.sendall(json.dumps(commitConent).encode())
                                commitResponse = worker.recv(1024)
                                print('recieved from server => ', commitResponse)

                        setResponse = {"type": "SET-RESPONSE", "success": isCommit}
                        conn.sendall(json.dumps(setResponse).encode())
                        print('Finished processing SET\n')                  

                    clean = strData.strip()
                    if clean=='' or clean == 'exit':
                        skt.close()
                        myClients.remove(skt)
                else:
                    print('Removing cli')
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
