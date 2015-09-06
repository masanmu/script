#!/usr/bin/env python

from multiprocessing import Process,Pool
import time
import threading
import optparse
import getpass
from core import ZabbixAPI

def get_options():
    usage = "Usage: %prog [options]"
    OptionParser = optparse.OptionParser
    parser = OptionParser(usage)
    
    parser.add_option("-s","--server",action="store",type="string",\
                    dest="server",help="(REQUIRED)Zabbix Server URL.")
    parser.add_option("-u","--user",action="store",type="string",\
                    dest="user",help="(REQUIRED)Username (Will prompt if not given).")
    parser.add_option("-p","--passwd",action="store",type="string",\
                    dest="passwd",help="(REQUIRED)Password (Will prompt if not given).")
    parser.add_option("-g","--groupname",action="store",type="string",\
                    dest="groupname",help="(REQUIRED)Host group name to find.")
    parser.add_option("-k","--key",action="store",type="string",\
                    dest="key",help="(REQUIRED)Key name to find.")
    parser.add_option("-H","--host",action="store",type="string",\
                    dest="host",help="(REQUIRED)Host name to find")
    parser.add_option("-l","--limit",action="store",type="string",\
                    dest="limit",default=1,help="(REQUIRED)Display how many data")
    parser.add_option("-a","--time_after",action="store",type="string",\
                    dest="time_after",help="Return only values that have been received after or at the given time (1970-01-01 00:00:00).")
    parser.add_option("-b","--time_before",action="store",type="string",\
                    dest="time_before",help="Return only values that have been received before or at the given time (1970-01-01 00:00:00).")
    parser.add_option("-t","--type",action="store",type="string",\
                    dest="type",default=0,help='''(REQUIRED)History object types to return. )
Possible values: 
0 - float
1 - string
2 - log
3 - integer
4 - text
Default: 0
''')

    options,args = parser.parse_args()

    if not options.server:
        options.server = raw_input("Server:")
    if not options.user:
        options.server = raw_input("Username:")
    if not options.passwd:
        options.passwd = getpass.getpass()

    return options,args


def runserver(zapi,hostname,hostid,key,type,time_after,time_before,limit):
    try:
        itemid=zapi.item.get({"output":"extend","hostids":hostid,"search":{"key_":key}})[0]['itemid']
        value=zapi.history.get({"output":"extend","history":type,"time_from":time_after,"time_till":time_before,"sortfield":"clock","sortorder":"DESC","itemids":itemid,"limit":limit})
        print hostname
        for i in range(int(limit)):
            print str(i+1)+"------->"+str(value[i]['value'])
    except Exception as e:
        pass
if __name__ == "__main__":
    localtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    options,args = get_options()
    server = options.server
    user = options.user
    passwd = options.passwd
    host = options.host
    groupname = options.groupname
    key = options.key
    type = options.type
    limit = options.limit
    if options.time_after:
        time_after = time.mktime(time.strptime(options.time_after,"%Y-%m-%d %H:%M:%S"))
    else:
        time_after = int(time.mktime(time.strptime("1970-01-01 08:00:00","%Y-%m-%d %H:%M:%S")))
    if options.time_before:
        time_before = time.mktime(time.strptime(options.time_before,"%Y-%m-%d %H:%M:%S"))
    else:
        time_before = int(time.time())
    
    zapi = ZabbixAPI(server,user,passwd)
   
    if groupname:
        for host in zapi.hostgroup.get({"selectHosts":"extend","filter":{"name":groupname}})[0]['hosts']:
            t = threading.Thread(target=runserver,args=(zapi,host['name'],host['hostid'],key,type,time_after,time_before,limit))
            t.start()
            t.join()
    elif host:
        try:
            hostid = zapi.host.get({"output":"hostid","filter":{"host":[host]}})[0]['hostid']
            itemid = zapi.item.get({"output":"extend","hostids":hostid,"search":{"key_":key}})[0]['itemid']
#            print zapi.history.get({"output":"extend","history":type,"time_from":time_after,"time_till":time_before,"sortfield":"clock","sortorder":"DESC","itemids":itemid,"limit":limit})
            value=zapi.history.get({"output":"extend","history":type,"time_from":time_after,"time_till":time_before,"sortfield":"clock","sortorder":"DESC","itemids":itemid,"limit":limit})
            print host
            for i in range(int(limit)):
                print str(i+1)+"------->"+str(value[i]['value'])
#            print host,value
        except Exception as e:
            pass
