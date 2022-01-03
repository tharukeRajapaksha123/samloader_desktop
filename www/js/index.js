function setTable(firmwares) {
    var table = document.querySelector("#firmware-table");
    firmwares.forEach(firmware => {
        //console.log(firmware)
        var tr = document.createElement("tr")
        var name = document.createElement("td")
        var model = document.createElement("td")
        var region = document.createElement("td")
        var version = document.createElement("td")
        var button = document.createElement("button")

        tr.setAttribute("id", firmware["firmware_version"])
        var status = firmware["status"]
        button.textContent = firmware["status"] === "found" ? "Download" : firmware["status"] === "downloaded" ? "Upload" : ""
        button.setAttribute("onclick", "startDownload('SM-T865','SEB')")

        name.textContent = firmware["filename"]
        model.textContent = firmware["model"]
        region.textContent = firmware["region"]
        version.textContent = firmware["firmware_version"]

        tr.appendChild(name)
        tr.appendChild(model)
        tr.appendChild(region)
        tr.appendChild(version)
        tr.append(button)

        table.appendChild(tr)
    })
}

async function fetchFirmwareData (){
    url = "http://127.0.0.1:7000/get-links"
    const response = await fetch(url);
    var data = await response.json()
    setTable(data)
}

fetchFirmwareData()

