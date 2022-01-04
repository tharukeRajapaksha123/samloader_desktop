var xhr = new XMLHttpRequest();
function addPost() {
    const title = document.getElementById("title").value
    const content = document.getElementById("content").value
    const meta_title = document.getElementById("meta-title").value
    const meata_description = document.getElementById("meta-description").value
    const download_link = document.getElementById("download-link").value

    const url = "https://sammfirms.herokuapp.com/add-post"
    const d = {
        "post_title": title,
        "content": content,
        "meta_title": meta_title,
        "meta_description": meata_description,
        "medifire_link": download_link,
        "gdrive_link": download_link,
        "megadrive_link": download_link,
    }
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    var res = xhr.send(JSON.stringify({
        data: d
    }));
}

const button = document.getElementById("submit-button")

button.addEventListener(("click"), function (e) {
    e.preventDefault()
    addPost()
})