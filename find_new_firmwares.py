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
    req = requests.get("http://127.0.0.1:7000/get-links")

  #  print(req.json())

    new_firmwares = getNewFirmWares()
    old_firmwares = req.json() 
    newest_firmwars = []
    for new_firmware in new_firmwares:
        for old_firmware in old_firmwares:
            if new_firmware["firmware_version"] == old_firmware["firmware_version"] :
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
                r = requests.post("http://127.0.0.1:7000/add-link",data=data)
                newest_firmwars.append(new_firmware)
                break
  
    

    return newest_firmwars


