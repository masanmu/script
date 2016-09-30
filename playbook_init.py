#!/usr/bin/env python

import os
import yaml
import optparse

def get_options():
    usage = "usage: %prog [options]"
    OptionParser = optparse.OptionParser
    parser = OptionParser(usage)

    parser.add_option("-s","--site",action="store",type="string",\
            dest="site",default="site.yml",help="playbook site file")

    options,args = parser.parse_args()
    return options,args

if __name__ == "__main__":
    options,args = get_options()
    workspace = "." if os.path.dirname(options.site) == "" else os.path.dirname(options.site)
    common = ["files","templates","tasks","handlers","vars","defaults","meta"]

    with open(options.site,"r") as f:
        site = f.read()

    site_dict = yaml.load(site)

    ###########init roles###################################
    for host in site_dict:
        try:
            for i in host["roles"]:
                try:
                    role = i["role"]
                except:
                    role = i
                for path in common:
                    mkdir=workspace+"/"+"roles"+"/"+role+"/"+path
                    if not os.path.exists(mkdir):
                        os.makedirs(mkdir)
                        if path != "files" and path != "templates":
                            os.mknod(mkdir+"/main.yml")
        except:
            os.mknod(workspace+"/"+host["include"]) 

    #############init variable################################
    vardir = workspace + "/group_vars/"
    if not os.path.exists(vardir):
        os.makedirs(vardir)
        os.mknod(vardir+"all")
    
    #############init hosts###################################
    for host in site_dict:
        try:
            with open(workspace+"/hosts","a+") as f:
                f.write("["+host["hosts"]+"]\n")
                f.flush()
        except:
            pass
