#!/usr/bin/env python
#coding:utf-8

import optparse
from getpass import getpass
from core import ZabbixAPI
from collections import namedtuple
from collections import deque

def get_options():
    usage = "usage:%prog [options]"
    OptionParser = optparse.OptionParser
    parser = OptionParser(usage)
    
    parser.add_option("-s","--server",action="store",type="string",\
                    dest="server",help="(REQUIRED)Zabbix Server URL.")
    parser.add_option("-u","--user",action="store",type="string",\
                    dest="user",help="(REQUIRED)Username (Will prompt if not given).")
    parser.add_option("-p","--passwd",action="store",type="string",\
                    dest="passwd",help="(REQUIRED)Password (Will prompt if not given).")
    parser.add_option("-n","--name",action="store",type="string",\
                    dest="name",help="(REQUIRED)Name of the screen.")
    parser.add_option("--hsize",action="store",type="string",\
                    dest="hsize",help="(REQUIRED)Width of the screen.")
    parser.add_option("--vsize",action="store",type="string",\
                    dest="vsize",help="(REQUIRED)Height of the screen.")
    parser.add_option("--host",action="store",type="string",\
                    dest="hostname",help="(REQUIRED)Host of the graph")
    parser.add_option("--graph",action="store",type="string",\
                    dest="graphname",help="(REQUIRED)Graph of the Host")
    parser.add_option("-T","--template",action="store_true",\
                    dest="template",help="(REQUIRED)Create screen on template")
    parser.add_option("-f","--file",action="store",dest="filename",\
                    metavar="FILE",help="(REQUIRED)Load values from input file. Specify - for standard input Each line of file contains whitespace delimited(<hostname>4space<groupname>)")
    
    options,args = parser.parse_args()
    if not options.server:
        options.server = raw_input('server http:')
    if not options.user:
        options.user = raw_input('zabbix user:')
    if not options.passwd:
        options.passwd = getpass()
    
    return options,args

def get_screenitems(position,graphid,screenitems):
    for l in position:
        Point = namedtuple("Point",['x','y'])
        p = Point(l[0],l[1])
        try:
            if p.y%2:
                d=dict(resourcetype=0,width=500,height=100,resourceid=graphid.popleft(),halign=1,valign=0,rowspan=1,colspan=1,x=p.y,y=p.x)
                screenitems.append(d)
            else:
                d=dict(resourcetype=0,width=500,height=100,resourceid=graphid.popleft(),halign=2,valign=0,rowspan=1,colspan=1,x=p.y,y=p.x)
                screenitems.append(d)
        except IndexError as e:
            return screenitems

if __name__ == "__main__":
    options,args = get_options()
    
    zapi = ZabbixAPI(options.server,options.user,options.passwd)
    
    name = options.name
    hsize = options.hsize
    vsize = options.vsize
    file = options.filename
    hostname = options.hostname
    graphname = options.graphname  
    template = options.template
    graphid = deque()
    screenitems = []
    if file:
        with open(file,'r')  as f:
            for line in f:
                l = line.split('    ')
                hostname = l[0].rstrip('\n').strip(' ')
                graphname = l[1].rstrip('\n').strip(' ')
                if not template:
                    hostid = zapi.host.get({"filter":{"host":hostname}})[0]['hostid']
                    graphid.append(zapi.graph.get({"output":"extend","hostids":hostid,"filter":{"name":graphname}})[0]['graphid'])
                else:
                    hostid = zapi.template.get({"filter":{"host":hostname}})[0]['templateid']
                    graphid.append(zapi.graph.get({"output":"extend","hostids":hostid,"filter":{"name":graphname}})[0]['graphid'])
        if template:
            position = [(row,cloumn) for row in xrange(int(vsize)) for cloumn in xrange(int(hsize))]
            screenitems = get_screenitems(position,graphid,screenitems)
            print screenitems
            zapi.templatescreen.create({"name":name,"templateid":hostid,"hsize":hsize,"vsize":vsize,"screenitems":screenitems})
        else:
            position = [(row,cloumn) for row in xrange(int(vsize)) for cloumn in xrange(int(hsize))]
            screenitems = get_screenitems(position,graphid,screenitems)
            print screenitems
            zapi.screen.create({"name":name,"hsize":hsize,"vsize":vsize,"screenitems":screenitems})
    else:
        if not template:
            hostid = zapi.host.get({"filter":{"host":hostname}})[0]['hostid']
            graphid = zapi.graph.get({"output":"extend","hostids":hostid,"filter":{"name":graphname}})[0]['graphid']
            screenitems.append(dict(resourcetype=0,width=1000,height=100,resourceid=graphid,halign=0,valign=0,rowspan=1,colspan=2,x=0,y=0))
            zapi.screen.create({"name":name,"hsize":hsize,"vsize":vsize,"screenitems":screenitems})
        else:
            hostid = zapi.template.get({"filter":{"host":template}})[0]['templateid']
            graphid=zapi.graph.get({"output":"extend","hostids":hostid,"filter":{"name":graphname}})[0]['graphid']
            screenitems.append(dict(resourcetype=0,width=1000,height=100,resourceid=graphid,halign=0,valign=0,rowspan=1,colspan=2,x=0,y=0))
            zapi.templatescreen.create({"name":name,"templateid":hostid,"hsize":hsize,"vsize":vsize,"screenitems":screenitems})
