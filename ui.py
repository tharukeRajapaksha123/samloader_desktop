import eel 
from datetime import datetime as dt

from main import main

from find_new_firmwares import compareFirmwares

#streams
startCalled = False 
pauseCalled = False 
resumeCalled = False
currentProcess = ""

downloadStarted = False
uploadStarted = False
filename = ""
downloadedFileSize = 0

@eel.expose
def startDownload(dev_model,dev_region):
    global downloadStarted,filename,downloadedFileSize
    res = main("download",dev_model,dev_region,False)
    filename = res["filename"]
    downloadedFileSize = res["downloadedfilesize"]
    print(res)
    downloadStarted = res["status"]
    

@eel.expose
def resumetDownload(dev_model,dev_region):
    main("download",dev_model,dev_region,True)


@eel.expose
def start():
    global startCalled,pauseCalled,resumeCalled
    startCalled = True 
    pauseCalled = False 
    resumeCalled = False

@eel.expose
def resume():
    global resumeCalled,pauseCalled,startCalled
    resumeCalled = True 
    startCalled = False 
    pauseCalled = False
@eel.expose
def pause():
    global pauseCalled,resumeCalled,resumeCalled
    pauseCalled = True 
    resumeCalled = False 
    resumeCalled = False
eel.init("www")
eel.start("index.html",block=False)
  
while True:
    if downloadStarted:
        eel.disableButton()
        eel.setFileName(filename)
        eel.setActivityText(downloadedFileSize,currentProcess)
    if startCalled:
        currentProcess = "s"
        downloadedFileSize = 60
        print("start called")
       
    if pauseCalled:
        print("pause called")
        currentProcess = ""
        
    if resumeCalled:
        print("resume called")
        currentProcess = "s"
        
    eel.sleep(1.0)

