import eel 
from datetime import datetime as dt

from main import main

from find_new_firmwares import compareFirmwares

downloadStarted = False

@eel.expose
def startDownload(dev_model,dev_region):
    global downloadStarted
    success = main("download",dev_model,dev_region,False)
    if success:
        downloadStarted = True

@eel.expose
def resumetDownload(dev_model,dev_region):
    main("download",dev_model,dev_region,True)



eel.init("www")
eel.start("index.html",block=False)
  
while True:
    eel.sleep(300.0)
