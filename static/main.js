var fileDrag = document.getElementById("file-drag");
var fileSelect = document.getElementById("file-upload");

fileDrag.addEventListener("dragover", fileDragHover, false);
fileDrag.addEventListener("dragleave", fileDragHover, false);
fileDrag.addEventListener("drop", fileSelectHandler, false);
fileSelect.addEventListener("change", fileSelectHandler, false);

var file = undefined;

function fileDragHover(e) {
    // prevent default behaviour
    e.preventDefault();
    e.stopPropagation();

    fileDrag.className = e.type === "dragover" ? "upload-box dragover" : "upload-box";
}

function fileSelectHandler(e) {
    // handle file selecting
    var files = e.target.files || e.dataTransfer.files;
    fileDragHover(e);
    file = files[0];
    console.log(file.name);
    displayFile(file);
}

var fileDisplay = document.getElementById("file-display");
var uploadCaption = document.getElementById("upload-caption");
var predResult = document.getElementById("pred-result");
var probability = document.getElementById("probability");
var loader = document.getElementById("loader");

function submitECGData() {
    // action for the submit button
    console.log("submit");

    if (!fileDisplay.value) {
        window.alert("请在上传前选择文件");
        return;
    }

    show(loader);
    fileDisplay.classList.add("loading");

    predictECGData(fileDisplay.value);
}

function displayFile(file) {
    readFileContent(file).then(content => {
        console.log(content);
        fileDisplay.value = content;
        uploadCaption.innerHTML = "文件名：" + file.name + "</br>" + "文件大小：" + file.size + "B";
        predResult.innerHTML = "";
        probability.innerHTML = "";
        fileDisplay.classList.remove("loading");
    }).catch(error => console.log(error));
}

function readFileContent(file) {
    const reader = new FileReader();
    return new Promise((resolve, reject) => {
        reader.onload = event => resolve(event.target.result);
        reader.onerror = error => reject(error);
        reader.readAsText(file);
    })
}

function clearECGData() {
    file = undefined;
    fileSelect.value = "";
    fileDisplay.value = "";
    predResult.innerHTML = "";
    probability.innerHTML = "";
    hide(loader);
    hide(predResult);
    hide(probability);
    uploadCaption.innerHTML = "拖拽上传 *.json 文件或点击选择文件";
    fileDisplay.classList.remove("loading");
}

function predictECGData(data) {
    fetch("/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }).then(resp => {
        if (resp.ok)
            resp.json().then(data => {
                console.log(data.success)
                if (data.success) {
                    displayResult(data);
                } else {
                    window.alert("Oops! Something went wrong.");
                }
            });
    }).catch(err => {
        console.log("An error occured", err.message);
        window.alert("Oops! Something went wrong.");
    });
}

function displayResult(data) {
    hide(loader);
    fileDisplay.classList.remove("loading");
    predResult.innerHTML = "分类结果：" + data.result;
    probability.innerHTML = "置信度：" + data.probability.map(toPercent);
    show(predResult);
    show(probability);
}

function toPercent(point) {
    var str = Math.floor(Number(point * 100000)) / 1000;
    str += "%";
    return str;
}

function hide(el) {
    el.classList.add("hidden");
}

function show(el) {
    el.classList.remove("hidden");
}