# Distributed-2PC-Database


**Purpose:** Distributed computing application using a 2PC (2 phase commit) Database

**Author:** Sami 

**Program Files:**  worker.py, coordinator.py, 

**Test Files:**     test_cli.py

# How to Run Program

**NOTE:** 

*To run this program you must have python3 installed*

*Run the worker.py first, followed by coordinator.py and then test_cli.py*

## 1. Run the workers
1. Open command line and specify directory containing worker.py file
2. Run command => ```python3 worker.py <portNum> ``` 
* * *Forexample=> ```python3 worker.py 8001 ``` 
Output => ```Running worker ... Connecting to 8001 ``` will be displayed in cmdline*
3. Repeat step 1 and 2 for as many workers as needed each with **different port numbers**

## 2. Run the coordinator
1. Open command line and specify directory containing coordinator.py file
2. Run command => ```python3 coordinator.py <portNum> <host:workerPortNum_1> ... <host:workerPortNum_n``` 
* * *Forexample => ``` python3 coordinator.py 5555 localhost:8001 localhost:8002``` 
Output => ```Running coordinator ... 			Starting server on port => 5555 				Connection made to worker w/ info => ('localhost', 8001) ``` will be diplayed in cmdline*

## 3. Run the client 
1. Open command line and specify directory containing test_cli.py file (Note this was provided by prof)
2. Run command => ```python3 test_cli.py <host:coordinatorPortNum> ``` 
* * *Forexample=> ```python3 test_cli.py localhost:5555 ``` 
Output => ```Connecting to localhost:5555
Welcome to the 3010 verifier shell.   Type help or ? to list commands. 3010> ``` will be displayed in cmdline*
3. Now you can run the get and set
___
**Notes:** 
1. Incase you get an error when connecting **test_cli.py** please specify ```host:coordinatorPortNum``` and that issues should be resolved
2. When running the client requests *you will be able to see outputs for your request in all the command line windows with the worker.py, co_ordinator.py and test_cli.py**
3. There is an attached **test_worker.py** which was provided by the prof which you can run to test the worker.py file
___
**Have a wonderful day!**



