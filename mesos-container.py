#!/usr/bin/env python

import json
import urllib2
import time
import re

response = urllib2.urlopen("http://127.0.0.1:9110/metrics")
metrics=response.read()
compile = re.compile(r".*framework_id=.*")
containers = compile.findall(metrics)
agg = {}
for metric in containers:
    name = metric.split("{")[0]
    tag = metric.split(",")[1].split(".")[0].split('"')[1]
    value = metric.split("}")[-1]
    agg[name+"&"+tag] = agg.get(name+"&"+tag,0) + float(value)
data = []
for key,value in agg.iteritems():
    info = {}
    info["endpoint"] = "a01.zabbix.b28.youku"
    info["metric"] = key.split("&")[0]
    info["timestamp"] = int(time.time())
    try:
        info["value"] = value
    except:
        continue
    info["counterType"] = "GAUGE"
    info["tags"] = "app="+key.split("&")[1]
    info["step"] = 60
    data.append(info)

request = urllib2.Request("http://127.0.0.1:1988/v1/push",data=json.dumps(data))
response = urllib2.urlopen(request)
print response
