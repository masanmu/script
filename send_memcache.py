#!/usr/bin/env python

import os
import sys
import memcache
import commands
import json
import commands
import IPy
import re
import optparse

def get_option():
    usage = "usage: %prog [options]"
    OptionParser = optparse.OptionParser
    parser = OptionParser(usage)

    parser.add_option("-s","--server",action="store",dest="zabbix_server",\
            type="string",help="Zabbix server")
    parser.add_option("-H","--hostname",action="store",dest="hostname",\
            type="string",help="Zabbix Monit Hostname")
    parser.add_option("-p","--port",action="store",dest="port",\
            type="string",help="Port of Monit Host")

    options,args = parser.parse_args()
    if not options.zabbix_server:
        raw_input("Please enter the server ZABBIX address:")
    return options


def get_stats(host,port):
    sum_stats=dict()
    mc=memcache.Client([host+":"+str(port)],debug=0)
    try:
        stats = mc.get_stats()[0][1]
    except:
        stats = {}
    if stats:
        for line in stats.iteritems():
            sum_stats[line[0]]=line[1]
    return sum_stats

def send_value(zabbix_server,memcache_stats,hostname,port):
    zabbix_sender = "/usr/bin/zabbix_sender"
    send_file = "/dev/shm/memcache_stats"
    if os.path.exists(send_file):
        os.remove(send_file)
    with open(send_file,"w+") as f:
        for stats in memcache_stats.iteritems():
            f.write("%s %s %s\n" % (hostname,stats[0]+"."+port,str(stats[1])))
    status,result = commands.getstatusoutput('%s -z %s -i %s' % (zabbix_sender,zabbix_server,send_file))
    os.remove(send_file)
    print result

if __name__=="__main__":
    options = get_option()
    zabbix_server = options.zabbix_server
    port = options.port
    if options.hostname:
        hostname = options.hostname
        memcache_stats = get_stats(hostname,port)
        print memcache_stats
        send_value(zabbix_server,memcache_stats,hostname,port)
        sys.exit(0)
    status,res = commands.getstatusoutput('/usr/bin/svn cat http:svn.example.com')
    compile = re.compile(r'env\[memcache_.*"(.*):%s' % port)
    m=compile.findall(res)
    host = m[0].split(":"+port)
    for hostname in host:
        memcache_stats = get_stats(hostname.strip(' '),port)
        send_value(zabbix_server,memcache_stats,hostname.strip(' '),port)
