# SPDX-License-Identifier: GPL-3.0+
# Copyright (C) 2020 nlscc

import json 
import os
import base64
import xml.etree.ElementTree as ET
from clint.textui import progress

from request import *
from crypt import *
from fusclient import *
from versionfetch import *

def checkUpdate(dev_model,dev_region):
    return getlatestver(dev_model,dev_region)

def main(method,dev_model,dev_region,resume):  
    if method == "download":
        fw_ver = checkUpdate(dev_model,dev_region)
        client = FUSClient()
        path, filename, size = getbinaryfile(client, fw_ver, dev_model, dev_region)
        initdownload(client,filename)
        cwd = os.getcwd()
        out = os.path.join(cwd, filename)
        dloffset = os.stat(out).st_size if resume else 0

        r,link,filename,headers = client.downloadfile(path+filename, dloffset)
        
        if r.status_code == 200 :
            return True
            # try:
            #     data = {
            #         "headers" : json.dumps(headers) ,
            #         "link" : link,
            #         "filename" : filename,
            #         "firmware_version" : fw_ver,
            #         "region" : dev_region,
            #         "model":dev_model,
            #     }
            #     r = requests.post("http://127.0.0.1:7000/add-link",data=data)
            #     print(r)
            #     return True
            # except :
            #     print("post request failed failed")
            #     return False
        else:
            print("failure")
            return False
        

    

def initdownload(client, filename):
    req = binaryinit(filename, client.nonce)
    resp = client.makereq("NF_DownloadBinaryInitForMass.do", req)

def getbinaryfile(client, fw, model, region):
    req = binaryinform(fw, model, region, client.nonce)
    resp = client.makereq("NF_DownloadBinaryInform.do", req)
    root = ET.fromstring(resp)
    status = int(root.find("./FUSBody/Results/Status").text)
    if status != 200:
        raise Exception("DownloadBinaryInform returned {}, firmware could not be found?".format(status))
    size = int(root.find("./FUSBody/Put/BINARY_BYTE_SIZE/Data").text)
    filename = root.find("./FUSBody/Put/BINARY_NAME/Data").text
    path = root.find("./FUSBody/Put/MODEL_PATH/Data").text
    return path, filename, size




