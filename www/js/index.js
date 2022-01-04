function startDownload(model,region){
  eel.startDownload(model,region)
}


function setTable(firmwares) {
  const totalDownloaded = document.querySelector(".total-downloaded");
  const totalUploaded = document.querySelector(".total-uploaded");
  var table = document.querySelector("#firmware-table");
  firmwares.forEach((firmware) => {
    //console.log(firmware)
    var tr = document.createElement("tr");
    var name = document.createElement("td");
    var model = document.createElement("td");
    var region = document.createElement("td");
    var version = document.createElement("td");
    var button = document.createElement("button");

    tr.setAttribute("id", firmware["firmware_version"]);
    var status = firmware["status"];
     
    if(status ==="found"){
      button.textContent = "DOWNLOAD"
      button.setAttribute("class","download-button")
      button.setAttribute("onclick", `startDownload('${firmware["model"]}','${firmware["region"]}')`);
    }else if(status === "downloaded"){
      button.textContent = "UPLOAD"
      button.setAttribute("class","upload-button")
      button.setAttribute("onclick", `startDownload('${firmware["model"]}','${firmware["region"]}')`);
    }else{
      button.textContent = ""
      button.setAttribute("class","restrict-button")
    }

    name.textContent = firmware["filename"];
    model.textContent = firmware["model"];
    region.textContent = firmware["region"];
    version.textContent = firmware["firmware_version"];

    tr.appendChild(name);
    tr.appendChild(model);
    tr.appendChild(region);
    tr.appendChild(version);
    tr.append(button);

    table.appendChild(tr);

    totalDownloaded.textContent = calculateTotalDownloads(status)
    totalUploaded.textContent = calculateTotalUploads(status)
  });
}

async function fetchFirmwareData() {
  url = "http://sammfirms.herokuapp.com/get-links";
  const response = await fetch(url);
  var data = await response.json();
  setTable(data);
}

function calculateTotalDownloads(status){
  var tot = 0
  if(status === "downloaded"){
    tot++
  }
  return tot
}

function calculateTotalUploads(status){
  var tot = 0
  if(status === "uploaded"){
    tot++
  }
  return tot
}

fetchFirmwareData();


function disableButton(){
  document.getElementsByClassName("download-button").disabled = true;
  document.getElementsByClassName("upload-button").disabled = true;
  document.getElementsByClassName("restrict-button").disabled = true;
}


function start(){
  eel.start()
}

function pause(){
  eel.pause()
}

function resume(){
  eel.resume()
}


function setActivityText(fileSize,status){
  const button = document.querySelector(".pause-resume-button")
  if(fileSize == 0){
    button.textContent = "Start"
    button.setAttribute("onclick","start()")
  }else{
    if(status === "s"){
      button.textContent = "PAUSE"
      button.setAttribute("onclick","pause()")
    }else{
      button.textContent = "RESUME"
      button.setAttribute("onclick","resume()")
    }
  }
}

eel.expose(disableButton)
eel.expose(setActivityText)