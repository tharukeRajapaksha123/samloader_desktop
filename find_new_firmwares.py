import json
import requests
from bs4 import BeautifulSoup
from tinydb import TinyDB

from main import main

db =TinyDB("data.json")

def getNewFirmWares():
    req = requests.get("https://www.sammobile.com/firmwares/")
    soup = BeautifulSoup(req.content,"html.parser")
    aLinks = soup.find_all("a", {"class": "table-link"})
    firmwares = []
 
    for link in aLinks:
        a = str(link).split(" ")
        b = a[2].split("/")
        firmware = {
            "device_name" : b[4],
            "model" : b[6],
            "region" : b[7],
            "firmware_version" : b[9],
            "status" : "found"
        }
        firmwares.append(firmware)
        
    return firmwares

def compareFirmwares():
    req = requests.get("https://sammfirms.herokuapp.com/get-links")

    new_firmwares = getNewFirmWares()
    old_firmwares = req.json() 
    newest_firmwars = []
   # print(new_firmwares)
   # print(old_firmwares)
    for new_firmware in new_firmwares:
        if(len(old_firmwares) == 0):
            data = {
                    "headers" :json.dumps({}) ,
                    "link" :new_firmware["status"],
                    "filename" : new_firmware["device_name"],
                    "firmware_version" : new_firmware["firmware_version"],
                    "region" : new_firmware["region"],
                    "model":new_firmware["model"],
                }
            r = requests.post("https://sammfirms.herokuapp.com/add-link",data=data)
        for old_firmware in old_firmwares:
           # print(new_firmware)
            if new_firmware["firmware_version"] == old_firmware["firmware_version"] and new_firmware["region"] ==old_firmware["region"]:
                break 
            else:
                data = {
                    "headers" :json.dumps({}) ,
                    "link" :new_firmware["status"],
                    "filename" : new_firmware["device_name"],
                    "firmware_version" : new_firmware["firmware_version"],
                    "region" : new_firmware["region"],
                    "model":new_firmware["model"],
                }
                r = requests.post("https://sammfirms.herokuapp.com/add-link",data=data)
                newest_firmwars.append(new_firmware)
                break
  
    
    #print(new_firmwares)
    return newest_firmwars


data = {
    "post_title" : "Test Post Title",
    "content" : "Test Post Content",
    "meta_title" : "Test Post Meta title",
    "meta_description" : "Test Post Meta meta_description",
    "medifire_link" : "Test Post Media Link",
    "gdrive_link" : "Test Post GDRIVE Link",
    "megadrive_link" : "Test Post Mega link",
}

requests.post("https://sammfirms.herokuapp.com/add-post",data=data)