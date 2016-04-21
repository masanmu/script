#!/usr/bin/python

import socket
import sys
import getpass
import optparse


def get_options():
    usage = 'usage: %prog [options]'
    OptionParser = optparse.OptionParser
    parser = OptionParser(usage)

    parser.add_option("-H","--host",action="store",type="string",\
                      dest="host",default="127.0.0.1",help="redis server")
    parser.add_option("-p","--port",action="store",type="string",\
                      dest="port",default="5678",help="redis port")

    options,args = parser.parse_args()
    return options,args

def kv_client(argvs,HOST,PORT):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    count = 0
    if argvs:
        s.sendall(argvs.strip('\n'))
        data = s.recv(4096)
        print data
    else:
        while 1:
            cmd = raw_input('Please input cmd:').rstrip(' ')
            if len(cmd) > 0:
                if cmd == 'exit':
                    sys.exit(0)
                elif cmd.split()[0].lower() == 'url':
                    if count == 0:
                        username = raw_input('Please input login username:').rstrip(' ')
                        password = getpass.getpass('Passwd:').rstrip(' ')
                    else:
                        pass
                    cmd = 'url '+username+' '+password+' '+cmd
                    s.sendall(cmd)
                    token_code = s.recv(4096)
                    if token_code == str(1):
                        count += 1
                        data = s.recv(4096)
                        print data
                    else:
                        print 'Your user name or password is not correct!'
                else:
                    s.sendall(cmd)
                    data = s.recv(4096)
                    print data

    s.close()

if __name__ == "__main__":
    options,args = get_options()

    HOST = options.host
    PORT = int(options.port)

    if len(args) > 0:
        argvs = (' ').join(args)
    else:
        argvs = False

    kv_client(argvs,HOST,PORT)

