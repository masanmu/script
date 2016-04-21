#!/usr/bin/env python

import socket
import commands
import getpass
import optparse
import sys
import sqlite3
import urllib2
import pickle
import logging

HOST = "127.0.0.1"
PORT = 5678
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='w')


#Initialize memory database, create a URL FILE, pass, CSV_FILE table
def init_database():
    try:
        db_conn = sqlite3.connect(':memmory:')
        cursor = db_conn.cursor()
        cursor.execute("create table if not exists URL_FILE (url varchar(255) NOT NULL,httpcode int NOT NULL,filesize int NOT NULL)")
        cursor.execute("create table if not exists KV_FILE (key varchar(255) NOT NULL,value varchar(255) NOT NULL,primary key (key))")
        logging.info('Initialize the database successfully')
    except:
        logging.error('Memory Database initialization failed')
    return cursor

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
#User login Detection
def get_token(username,password):
    username = username
    passwd = password
    with open('auth.conf') as f:
        for line in f:
            if passwd == line.split(':')[1].strip('\n') and username == line.split(':')[0].strip(' '):
                return 1
        return 0
#set function definition
def set(cursor,conn,key,value):
    try:
        cursor.execute("insert into KV_FILE (key,value) values(?,?)",(key,value))
        conn.sendall('Add KV Done!')
        logging.info('Add %s = %s to redis' % (key,value))
    except:
        logging.error('Failed to add key = value')

#get function definition
def get(cursor,conn,key):
    try:
        cursor.execute("select value from KV_FILE where key == ?",(key,))
        value = cursor.fetchall()
        conn.sendall(value[0][0])
        logging.info('retrieve data %s',value[0][0])
    except:
        conn.sendall(' ')

#url function definition
def url(cursor,conn,data):
    try:
        username = data.split()[1]
        password = data.split()[2]
        token_code = get_token(username,password)
        conn.sendall(str(token_code))
    except:
        logging.error('Not enter a username or password')
        conn.sendall('0')
        return
    if not token_code:
        return
    name = data.split()[-2]
    try:
        cursor.execute("select httpcode,filesize from URL_FILE where url == ?",(name,))
        URL_NAME = cursor.fetchall()
        conn.sendall('filesize:%s httpcode %s' % (str(URL_NAME[0][1]),str(URL_NAME[0][0])))
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
            filesize = dict(response.headers).get('content-length', 0)
            httpcode = response.getcode()
            cursor.execute("insert into URL_FILE(url,httpcode,filesize)values(?,?,?)", (url,httpcode,filesize))
            conn.sendall('Add name')


#redis server function
def connect(cursor,HOST,PORT):

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen(1)

    while True:
        conn,addr = s.accept()
        print 'Connected by',addr
        logging.info('Connected by %s port %s' % (addr[0],addr[1]))
        while True:
            data = conn.recv(1024)
            logging.info('Receiving data over the "%s"' % data)
            try:
                method = data.split()[0]
            except:
                conn.close()
                break
            if method == 'set':
                try:
                    set(cursor,conn,data.split()[1],data.split()[2])
                except:
                    conn.sendall('Usage:set key value')
                    pass
            elif method == 'get':
                get(cursor,conn,data.split()[1])
            elif method.lower() == 'url':
                url(cursor,conn,data)
            else:
                cmd_status,cmd_result = commands.getstatusoutput(data)
                if cmd_status:
                    conn.sendall('Error command')
                else:
                    conn.sendall(cmd_result)

    conn.close()

if __name__ == '__main__':

    options,args = get_options()

    HOST = options.host
    PORT = int(options.port)

    cursor = init_database()
    connect(cursor,HOST,PORT)
    cursor.close()

