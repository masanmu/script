#!/usr/bin/env python

import socket
import commands
import getpass
import optparse
import sys
import urllib2
import pickle

HOST = "127.0.0.1"
PORT = 5678
kv_file = 'kv'
url_file = 'url'
redis = dict()
url_name = dict()

def get_options():
    usage = 'usage %prong [options]'
    OptionParser = optparse.OptionParser
    parser = OptionParser(usage)

    parser.add_option('-H','--host',action='store',type='string',\
                      dest='host',default='127.0.0.1',help='redis server')
    parser.add_option('-p','--port',action='store',type='string',\
                      dest='port',default=5678,help='redis port')

    options,args = parser.parse_args()

    return options,args

def get_token(username,password):
    username = username
    passwd = password
    with open('auth.conf') as f:
        for line in f:
            if passwd == line.split(':')[1].strip('\n') and username == line.split(':')[0].strip(' '):
                return 1
        return 0

if __name__ == '__main__':

    options,args = get_options()

    HOST = options.host
    PORT = int(options.port)

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen(1)

    while True:
        conn,addr = s.accept()
        print 'Connected by',addr
        while True:
            data = conn.recv(1024)
            try:
                method = data.split()[0]
            except:
                conn.close()
                break
            if method == 'set':
                redis[data.split()[1]] = data.split()[2]
                with open(kv_file,'wb') as f:
                    pickle.dump(redis,f,True)
                conn.sendall('Add KV Done!')
            elif method == 'get':
                try:
                    with open(kv_file) as f:
                        redis = pickle.load(f)
                    value = redis[data.split()[1]]
                    conn.sendall(value)
                except:
                    conn.sendall(' ')
            elif method.lower() == 'url':
                username = data.split()[1]
                password = data.split()[2]
                token_code = get_token(username,password)
                conn.sendall(str(token_code))
                if token_code:
                    name = data.split()[-2]
                    try:
                        with open(url_file) as f:
                            url_name = pickle.load(f)
                        conn.sendall('filesize:%s httpcode %s' % (str(url_name[name]['filesize']),str(url_name[name]['httpcode'])))
                    except:
                        url = data.split()[-1]
                        opener = urllib2.build_opener()
                        request = urllib2.Request(url)
                        request.get_method = lambda: 'HEAD'
                        try:
                            response = opener.open(request)
                            response.read()
                        except Exception, e:
                            conn.sendall('%s %s' % (url,e))
                        else:
                            url_name[name]=dict()
                            url_name[name]['filesize'] = dict(response.headers).get('content-length', 0)
                            url_name[name]['httpcode'] = response.getcode()
                            with open(url_file,'wb') as f:
                                pickle.dump(url_name,f,True)
                            conn.sendall('Add name')
                else:
                    pass


            else:
                cmd_status,cmd_result = commands.getstatusoutput(data)
                if cmd_status:
                    conn.sendall('Error command')
                else:
                    conn.sendall(cmd_result)

    conn.close()
