const downloadSpeed = document.querySelector(".download-speed");
const uploadSpeed = document.querySelector(".upload-speed");
const totalDownloaded = document.querySelector(".total-downloaded");
const totalUploaded = document.querySelector(".total-uploaded");

const downloadSlider = document.querySelector(".download-slider");
const uploadSlider = document.querySelector(".upload-slider");
const downloadProgressValue = document.querySelector(
  ".download-progress-value"
);
const uploadProgressValue = document.querySelector(".upload-progress-value");

// use this function to change values in data circles
// elem = html element, val = value
const changeData = (elem, val) => {
  elem.textContent = val;
};

// use this function to change progress bar values
const changeProgress = (elem, val) => {
  elem.style.width = `${val}%`;
  if (elem === downloadSlider) {
    downloadProgressValue.textContent = `${val}%`;
  }

  if (elem === uploadSlider) {
    uploadProgressValue.textContent = `${val}%`;
  }
};

// examples
changeData(downloadSpeed, 30);
changeData(uploadSpeed, 15);
changeData(totalDownloaded, 100);
changeData(totalUploaded, 45);
changeProgress(downloadSlider, 78);
changeProgress(uploadSlider, 24);
