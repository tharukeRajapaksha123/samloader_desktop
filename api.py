from fastapi import FastAPI
import base64
from Cryptodome.Cipher import AES

import hashlib
import xml.etree.ElementTree as ET

from clint.textui import progress

import requests
from request import binaryinform

from versionfetch import normalizevercode

import json
import os
# Constant key input values.
KEY_1 = "hqzdurufm2c8mf6bsjezu1qgveouv7c7"
KEY_2 = "w13r4cvf4hctaujv"

# PKCS#7 padding functions.
pkcs_unpad = lambda d: d[:-d[-1]]
pkcs_pad = lambda d: d + bytes([16 - (len(d) % 16)]) * (16 - (len(d) % 16))

def aes_encrypt(inp: bytes, key: bytes) -> bytes:
    """ Perform an AES-CBC encryption. Encrypts /inp/ with key /key/. """
    enc_iv = key[:16] # IV is first 16 bytes of key
    cipher = AES.new(key, AES.MODE_CBC, enc_iv)
    return cipher.encrypt(pkcs_pad(inp))

def aes_decrypt(inp: bytes, key: bytes) -> bytes:
    """ Perform an AES-CBC decryption. Decrypts /inp/ with key /key/. """
    enc_iv = key[:16]
    cipher = AES.new(key, AES.MODE_CBC, enc_iv)
    return pkcs_unpad(cipher.decrypt(inp))

def derive_key(nonce: str) -> bytes:
    """ Calculate the AES key from the FUS input nonce. """
    key = ""
    # First 16 bytes are offsets into KEY_1
    for i in range(16):
        key += KEY_1[ord(nonce[i]) % 16]
    # Last 16 bytes are static
    key += KEY_2
    return key.encode()

def getauth(nonce: str) -> str:
    """ Calculate the response token from a given nonce. """
    nkey = derive_key(nonce)
    auth_data = aes_encrypt(nonce.encode(), nkey)
    return base64.b64encode(auth_data).decode()

def decryptnonce(inp: str) -> str:
    """ Decrypt the nonce returned by the server. """
    inp_data = base64.b64decode(inp)
    nonce = aes_decrypt(inp_data, KEY_1.encode()).decode()
    return nonce

#request.py
def getlogiccheck(inp: str, nonce: str) -> str:
    """ Calculate the request checksum for a given input and nonce. """
    if len(inp) < 16:
        raise Exception("getlogiccheck() input too short")
    out = ""
    for c in nonce:
        out += inp[ord(c) & 0xf]
    return out

def build_reqhdr(fusmsg: ET.Element):
    """ Build the FUSHdr of an XML message. """
    fushdr = ET.SubElement(fusmsg, "FUSHdr")
    ET.SubElement(fushdr, "ProtoVer").text = "1.0"

def build_reqbody(fusmsg: ET.Element, params: dict):
    """ Build the FUSBody of an XML message. """
    fusbody = ET.SubElement(fusmsg, "FUSBody")
    fput = ET.SubElement(fusbody, "Put")
    for tag, value in params.items():
        setag = ET.SubElement(fput, tag)
        sedata = ET.SubElement(setag, "Data")
        sedata.text = str(value)

def binaryinform(fwv: str, model: str, region: str, nonce: str) -> str:
    """ Build a BinaryInform request. """
    fusmsg = ET.Element("FUSMsg")
    build_reqhdr(fusmsg)
    build_reqbody(fusmsg, {
        "ACCESS_MODE": 2,
        "BINARY_NATURE": 1,
        "CLIENT_PRODUCT": "Smart Switch",
        "DEVICE_FW_VERSION": fwv,
        "DEVICE_LOCAL_CODE": region,
        "DEVICE_MODEL_NAME": model,
        "LOGIC_CHECK": getlogiccheck(fwv, nonce)
    })
    return ET.tostring(fusmsg)

def binaryinit(filename: str, nonce: str) -> str:
    """ Build a BinaryInit request. """
    fusmsg = ET.Element("FUSMsg")
    build_reqhdr(fusmsg)
    checkinp = filename.split(".")[0][-16:]
    build_reqbody(fusmsg, {
        "BINARY_FILE_NAME": filename,
        "LOGIC_CHECK": getlogiccheck(checkinp, nonce)
    })
    return ET.tostring(fusmsg)




#crypt.py
# PKCS#7 unpad
unpad = lambda d: d[:-d[-1]]

def getv4key(version, model, region):
    """ Retrieve the AES key for V4 encryption. """
    client = FUSClient()
    version = normalizevercode(version)
    req = binaryinform(version, model, region, client.nonce)
    resp = client.makereq("NF_DownloadBinaryInform.do", req)
    root = ET.fromstring(resp)
    fwver = root.find("./FUSBody/Results/LATEST_FW_VERSION/Data").text
    logicval = root.find("./FUSBody/Put/LOGIC_VALUE_FACTORY/Data").text
    deckey = getlogiccheck(fwver, logicval)
    return hashlib.md5(deckey.encode()).digest()

def getv2key(version, model, region):
    """ Calculate the AES key for V2 (legacy) encryption. """
    deckey = region + ":" + model + ":" + version
    return hashlib.md5(deckey.encode()).digest()

def decrypt_progress(inf, outf, key, length):
    """ Decrypt a stream of data while showing a progress bar. """
    cipher = AES.new(key, AES.MODE_ECB)
    if length % 16 != 0:
        raise Exception("invalid input block size")
    chunks = length//4096+1
    for i in progress.bar(range(chunks)):
        block = inf.read(4096)
        if not block:
            break
        decblock = cipher.decrypt(block)
        if i == chunks - 1:
            outf.write(unpad(decblock))
        else:
            outf.write(decblock)

#fusclient.py
class FUSClient:
    """ FUS API client. """
    def __init__(self):
        self.auth = ""
        self.sessid = ""
        self.makereq("NF_DownloadGenerateNonce.do") # initialize nonce
    def makereq(self, path: str, data: str = "") -> str:
        """ Make a FUS request to a given endpoint. """
        authv = 'FUS nonce="", signature="' + self.auth + '", nc="", type="", realm="", newauth="1"'
        req = requests.post("https://neofussvr.sslcs.cdngc.net/" + path, data=data,
                            headers={"Authorization": authv, "User-Agent": "Kies2.0_FUS"},
                            cookies={"JSESSIONID": self.sessid})
        # If a new NONCE is present, decrypt it and update our auth token.
        if "NONCE" in req.headers:
            self.encnonce = req.headers["NONCE"]
            self.nonce = decryptnonce(self.encnonce)
            self.auth = getauth(self.nonce)
        # Update the session cookie if needed.
        if "JSESSIONID" in req.cookies:
            self.sessid = req.cookies["JSESSIONID"]
        req.raise_for_status()
        return req.text
    async def downloadfile(self, filename: str, start: int = 0) -> requests.Response:
        """ Make a FUS cloud request to download a given file. """
        # In a cloud request, we also need to pass the server nonce.
        authv = 'FUS nonce="' + self.encnonce + '", signature="' + self.auth \
            + '", nc="", type="", realm="", newauth="1"'
        headers = {"Authorization": authv, "User-Agent": "Kies2.0_FUS"}
        if start > 0:
            headers["Range"] = "bytes={}-".format(start)
        link = "http://cloud-neofussvr.sslcs.cdngc.net/NF_DownloadBinaryForMass.do"
        req = requests.get(link,
                           params="file=" + filename, headers=headers, stream=True)
        req.raise_for_status()
       # print("download link is ",req.status_code)
       # print("headers ",headers)
        return req,link,filename,headers

#versionfetch.py
def normalizevercode(vercode: str) -> str:
    """ Normalize a version code to four-part form. """
    ver = vercode.split("/")
    if len(ver) == 3:
        ver.append(ver[0])
    if ver[2] == "":
        ver[2] = ver[0]
    return "/".join(ver)

def getlatestver(model: str, region: str) -> str:
    """ Get the latest firmware version code for a model and region. """
    req = requests.get("https://fota-cloud-dn.ospserver.net/firmware/" \
        + region + "/" + model + "/version.xml")
    req.raise_for_status()
    root = ET.fromstring(req.text)
    vercode = root.find("./firmware/version/latest").text
    if vercode is None:
        raise Exception("No latest firmware found")
    return normalizevercode(vercode)


#main.py
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

async def checkUpdate(dev_model,dev_region):
    return getlatestver(dev_model,dev_region)

async def main(method,dev_model,dev_region,resume):  
    if method == "download":
        fw_ver =await checkUpdate(dev_model,dev_region)
        client = FUSClient()
        path, filename, size = getbinaryfile(client, fw_ver, dev_model, dev_region)
        print("path is ",path)
        print("file name is ",filename)
        print("file size is ",size)
        initdownload(client,filename)
        cwd = os.getcwd()
        out = os.path.join(cwd, filename)
        dloffset = os.stat(out).st_size if resume else 0

        r,link,filename,headers =await client.downloadfile(path+filename, dloffset)
        
        if r.status_code == 200 :
            try:
                data = {
                    "headers" : json.dumps(headers) ,
                    "link" : link,
                    "filename" : filename,
                    "firmware_version" : fw_ver,
                    "region" : dev_region,
                    "model":dev_model,
                }
                r = requests.post("http://127.0.0.1:7000/add-link",data=data)
                return True
            except :
                print("post request failed failed")
                return False
        else:
            return False


app = FastAPI()

@app.get("/")
def home():
    return {"server_status" : "working"}

@app.get("/check-updates/{model}/{region}")
async def checkForUpdates(model : str,region:str):
    #print(model,region)
    file_response =await main("download",model,region,False)
    if file_response:
        return {"status_code" : "success","status" : 200}
    
    else : 
        return {"status_code" : "failed","status" : 400}

