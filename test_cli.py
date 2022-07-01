import cmd
import sys
import re
import json
import socket


class TestShell(cmd.Cmd):
    intro = 'Welcome to the 3010 verifier shell.   Type help or ? to list commands.\n'
    prompt = 'Hello > '
    coordinatorSock = None

    def preloop(self) -> None:
        '''
        Connect to the coordinator
        '''
        try:
            print("Connecting to " + sys.argv[1])
            self.coordinatorSock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            parts = sys.argv[1].split(':')
            # there is a more pythonic way. Not today!
            who = (parts[0], int(parts[1]))
            self.coordinatorSock.connect(who)
            
        except Exception as e:
            print("Could not connnet. Quitting")
            print(e)
            sys.exit(1)

    def do_set(self, arg):
        '''
        Set a value in the database: set key value
        '''
        matches = re.match("(\S+)\s+(\S+)", arg)
        if matches is None:
            print("set requires two arguments: the key and value")
        else:
            key = matches.group(1)
            value = matches.group(2)

            try:
                content = {"type": "SET", "key": key, "value": value}

                self.coordinatorSock.sendall(json.dumps(content).encode())
                # wait for reply
                print(self.coordinatorSock.recv(1024))
            except Exception as e:
                print("Error sending/receiving")
                print(e)

    def do_get(self, arg):
        '''
        Set a value in the database: set key value
        '''

        if len(arg) == 0:
            print("set requires two arguments: the key and value")
        else:

            try:
                content = {"type": "GET", "key": arg}

                self.coordinatorSock.sendall(json.dumps(content).encode())
                # wait for reply
                print(self.coordinatorSock.recv(1024))
            except Exception as e:
                print("Error sending/receiving")
                print(e)

    def do_exit(self, arg):
        print('Later, gator.')
        return True

    def do_EOF(self, arg):
        print('The cool way to exit!')
        return True

    def postloop(self) -> None:
        try:
            if self.coordinatorSock is not None:
                self.coordinatorSock.close()
        except:
            print("Failed to ")


if __name__ == '__main__':
    TestShell().cmdloop()
