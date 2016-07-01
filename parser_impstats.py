#!/usr/bin/env python

import sys
import time
import urllib2
import json
import re

while 1:
	line = sys.stdin.readline().rstrip("\n")
	try:
		impstatus = eval(line.split("rsyslogd-pstats: @cee:")[1])
	except:
		try:
			impstatus = eval(line.split("rsyslogd-pstats:")[1])
		except:
			continue
	name = impstatus["name"]
	if name.find("action_") < 0 and name.find("main Q") < 0:
		continue	
	endpoint = line.split(" ")[1]
	data = []
	for key in ["size","enqueued","full","discarded.full","discarded.nf","maxqsize","processed","failed"]:
		info ={}
		info["endpoint"] = endpoint
		info["metric"] = name+" "+key
		info["timestamp"] = int(time.time())
                try:
		    info["value"] = impstatus[key]
                except:
                    continue
		info["counterType"] = "GAUGE"
		if endpoint.find("rsyslog.forward") < 0:
			info["tags"] = "rsyslog=impstatus,role=front"
		else:
			info["tags"] = "rsyslog=impstatus,role=forward"
		info["step"] = 300
		data.append(info)
	request = urllib2.Request("http://10.100.11.32:1988/v1/push",data=json.dumps(data))
        response = urllib2.urlopen(request)

