#!/usr/bin/env python

import gethost
import os
import sys
import memcache
import commands
import json
import IPy
import re
import optparse

def get_option():
    usage = "usage: %prog [options]"
    OptionParser = optparse.OptionParser
    parser = OptionParser(usage)

    parser.add_option("-s","--server",action="store",dest="zabbix_server",\
            type="string",help="Zabbix server")
    parser.add_option("-c","--config",dest="zabbix_config",\
            metavar="file",help="Zabbix agentd conf")
    parser.add_option("-o","--operator",dest="operator",\
            type="string",help="Three operators.Options:lt,yd,dx")
    parser.add_option("-v","--version",dest="version",default="v5",\
            type="string",help="weibo version number.Options:v4,v5,v6")

    options,args = parser.parse_args()
    if not options.zabbix_server:
        raw_input("Please enter the server ZABBIX address.:")
    return options

def get_stats(mc_host):
    sum_stats=dict()
    for IP in mc_host:
        ip = IP.split(':')[0]
        port = IP.split(':')[1]
        mc=memcache.Client([ip+":"+str(port)],debug=0)
        try:
            stats = mc.get_stats()[0][1]
        except:
            stats = {}
        if stats:
            for line in stats.iteritems():
                key = line[0]
                value = line[1]
                try:
                    sum_stats[key] = float(sum_stats.get(key,0)) + float(value)
                except:
                    pass

    return sum_stats

def get_host(result,port):
    twem = {"18500":"weibo_session","18501":"weibo_default","18502":"weibo_upload","18503":"weibo_tag","18504":"weibo_captcha"}
    result = json.loads(result)
    host_list = list()
    for ip in result[twem[str(port)]].iterkeys():
        try:
            IP = ip.split(':')[0]
            if IPy.IP(IP):
                host_list.append(ip)
        except:
            pass
    return host_list

def send_value(zabbix_server,zabbix_config,mc_18500_stats,mc_18501_stats,mc_18502_stats,mc_18503_stats,mc_18504_stats,hostname):
	zabbix_sender = "/usr/bin/zabbix_sender"
	send_file = "/dev/shm/mc_stats"
	if os.path.exists(send_file):
		os.remove(send_file)
	port = 18500
	with open(send_file,"w+") as f:
		for port_stats in mc_18500_stats,mc_18501_stats,mc_18502_stats,mc_18503_stats,mc_18504_stats:
			for mc in port_stats.iteritems():
				f.write("%s %s %.4f\n" % (hostname,"mc_"+str(port)+"_stats_"+mc[0],float(mc[1])))
			port += 1
	stattus,result = commands.getstatusoutput('%s -z %s -i %s' % (zabbix_sender,zabbix_server,send_file))
	os.remove(send_file)
	print result

if __name__=="__main__":
    options = get_option()
    zabbix_server = options.zabbix_server
    zabbix_config = options.zabbix_config
    version = options.version
    operator = options.operator
    if operator == "lt":
        hostname = "mweibo-web-v5-chinaunicom"
    elif operator == "dx":
        hostname = "mweibo-web-v5-chinanet"
    elif operator == "yd":
        hostname = "mweibo-web-v5-chinamobile"
    host_list=gethost.v5(operator)
    status,result = commands.getstatusoutput("nc -w 5 %s 22222" % host_list)
    if status:
        sys.exit(-1)
    mc_18500 = get_host(result,18500)
    mc_18500_stats = get_stats(mc_18500)
    mc_18501 = get_host(result,18501)
    mc_18501_stats = get_stats(mc_18501)
    mc_18502 = get_host(result,18502)
    mc_18502_stats = get_stats(mc_18502)
    mc_18503 = get_host(result,18503)
    mc_18503_stats = get_stats(mc_18503)
    mc_18504 = get_host(result,18504)
    mc_18504_stats = get_stats(mc_18504)
    send_value(zabbix_server,zabbix_config,mc_18500_stats,mc_18501_stats,mc_18502_stats,mc_18503_stats,mc_18504_stats,hostname)
