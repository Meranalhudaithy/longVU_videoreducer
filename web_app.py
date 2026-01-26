import os
import shutil
import subprocess
import uuid
import sys

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse


BASE = os.path.dirname(__file__)

UPLOAD = os.path.join(BASE, "uploads")
OUTPUT = os.path.join(BASE, "outputs")

os.makedirs(UPLOAD, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>
<html>
<head>
<title>LongVU Video Reducer</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

<style>

* {
    box-sizing: border-box;
    font-family: 'Inter', sans-serif;
}

body {
    margin: 0;
    min-height: 100vh;
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    padding: 20px;
}

/* Animated Background */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(56, 189, 248, 0.2) 0%, transparent 50%);
    pointer-events: none;
    z-index: -1;
}

/* Main Card Container */
.card {
    width: 100%;
    max-width: 480px;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 40px 35px;
    box-shadow: 
        0 25px 50px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* Header */
.header {
    text-align: center;
    margin-bottom: 35px;
}

.logo-container {
    width: 70px;
    height: 70px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 18px;
    font-size: 32px;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

h1 {
    margin: 0;
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.sub {
    color: rgba(255, 255, 255, 0.6);
    margin-top: 8px;
    font-size: 14px;
    font-weight: 400;
}

/* Upload Zone - Square Shape */
.drop {
    aspect-ratio: 1 / 1;
    max-width: 280px;
    width: 100%;
    margin: 0 auto;
    border: 2px dashed rgba(139, 92, 246, 0.5);
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: rgba(139, 92, 246, 0.05);
    position: relative;
    overflow: hidden;
}

.drop::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(56, 189, 248, 0.1) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.drop:hover {
    border-color: #8b5cf6;
    transform: translateY(-3px);
    box-shadow: 
        0 15px 40px rgba(139, 92, 246, 0.25),
        0 0 0 4px rgba(139, 92, 246, 0.1);
}

.drop:hover::before {
    opacity: 1;
}

.drop.dragover {
    border-color: #38bdf8;
    background: rgba(56, 189, 248, 0.1);
    transform: scale(1.02);
}

.drop-content {
    position: relative;
    z-index: 1;
    text-align: center;
    padding: 20px;
}

.drop-icon {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 16px;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.35);
}

.drop-icon i {
    font-size: 24px;
    color: white;
}

.drop-text {
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 6px;
}

.drop-hint {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.5);
}

/* File Info */
.file-info {
    margin-top: 20px;
    padding: 14px 18px;
    background: rgba(139, 92, 246, 0.1);
    border-radius: 12px;
    font-size: 13px;
    text-align: left;
    display: none;
    border: 1px solid rgba(139, 92, 246, 0.2);
}

.file-info.show {
    display: block;
    animation: fadeIn 0.3s ease;
}

.file-info .file-name {
    font-weight: 600;
    color: #c4b5fd;
    margin-bottom: 4px;
    word-break: break-all;
}

.file-info .file-size {
    color: rgba(255, 255, 255, 0.6);
}

/* Button */
button {
    margin-top: 25px;
    width: 100%;
    padding: 16px 24px;
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    border: none;
    border-radius: 14px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.35);
}

button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 12px 35px rgba(139, 92, 246, 0.45);
}

button:active:not(:disabled) {
    transform: translateY(0);
}

button:disabled {
    background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
    box-shadow: none;
    cursor: not-allowed;
    opacity: 0.7;
}

button i {
    font-size: 18px;
}

/* Progress */
.progress-container {
    margin-top: 25px;
    display: none;
}

.progress-container.show {
    display: block;
    animation: fadeIn 0.3s ease;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.7);
}

.progress {
    width: 100%;
    height: 10px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 20px;
    overflow: hidden;
}

.bar {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #8b5cf6 0%, #38bdf8 100%);
    border-radius: 20px;
    transition: width 0.4s ease;
    position: relative;
}

.bar::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.3),
        transparent
    );
    animation: shimmer 1.5s infinite;
}

/* Status */
#msg {
    margin-top: 20px;
    min-height: 24px;
    font-size: 14px;
    text-align: center;
}

#msg a {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #38bdf8;
    text-decoration: none;
    padding: 12px 24px;
    background: rgba(56, 189, 248, 0.1);
    border-radius: 10px;
    margin-top: 10px;
    transition: all 0.3s ease;
    border: 1px solid rgba(56, 189, 248, 0.3);
}

#msg a:hover {
    background: rgba(56, 189, 248, 0.2);
    transform: translateY(-2px);
}

.success-icon {
    font-size: 48px;
    margin-bottom: 15px;
    animation: bounce 0.5s ease;
}

input { display: none; }

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

@keyframes bounce {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.spinner {
    animation: spin 1s linear infinite;
}

/* Responsive */
@media (max-width: 520px) {
    .card {
        padding: 30px 20px;
        border-radius: 20px;
    }
    
    h1 {
        font-size: 24px;
    }
    
    .drop {
        max-width: 220px;
    }
    
    .logo-container {
        width: 60px;
        height: 60px;
        font-size: 28px;
    }
}

@media (max-width: 360px) {
    .card {
        padding: 25px 15px;
    }
    
    .drop {
        max-width: 180px;
    }
    
    h1 {
        font-size: 22px;
    }
}

</style>
</head>

<body>

<div class="card">

    <div class="header">
        <div class="logo-container">🎬</div>
        <h1>LongVU Reducer</h1>
        <p class="sub">Optimize videos for AI models and storage</p>
    </div>

    <form id="f">

        <label class="drop" id="dropzone">
            <div class="drop-content">
                <div class="drop-icon">
                    <i class="fa-solid fa-cloud-arrow-up"></i>
                </div>
                <div class="drop-text">Drop your video here</div>
                <div class="drop-hint">or click to browse</div>
            </div>
            <input id="file" type="file" accept="video/*">
        </label>

        <div class="file-info" id="info">
            <div class="file-name" id="fileName"></div>
            <div class="file-size" id="fileSize"></div>
        </div>

        <button id="btn" type="submit">
            <i class="fa-solid fa-compress"></i>
            Reduce Video
        </button>

    </form>

    <div class="progress-container" id="progContainer">
        <div class="progress-label">
            <span>Processing...</span>
            <span id="percent">0%</span>
        </div>
        <div class="progress">
            <div class="bar" id="bar"></div>
        </div>
    </div>

    <div id="msg"></div>

</div>


<script>

const f = document.getElementById("f");
const msg = document.getElementById("msg");
const btn = document.getElementById("btn");
const info = document.getElementById("info");
const bar = document.getElementById("bar");
const progContainer = document.getElementById("progContainer");
const fileInput = document.getElementById("file");
const dropzone = document.getElementById("dropzone");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const percent = document.getElementById("percent");

/* Drag and Drop */
['dragenter', 'dragover'].forEach(e => {
    dropzone.addEventListener(e, (ev) => {
        ev.preventDefault();
        dropzone.classList.add('dragover');
    });
});

['dragleave', 'drop'].forEach(e => {
    dropzone.addEventListener(e, (ev) => {
        ev.preventDefault();
        dropzone.classList.remove('dragover');
    });
});

dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length) {
        fileInput.files = files;
        showFileInfo(files[0]);
    }
});

/* Show file info */
fileInput.onchange = () => {
    const file = fileInput.files[0];
    if (file) showFileInfo(file);
};

function showFileInfo(file) {
    const size = (file.size / 1024 / 1024).toFixed(2);
    fileName.textContent = '📄 ' + file.name;
    fileSize.textContent = '📦 ' + size + ' MB';
    info.classList.add('show');
}

/* Submit */
f.onsubmit = async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        msg.innerHTML = '<span style="color:#f87171">⚠️ Please select a video first</span>';
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner spinner"></i> Processing...';
    progContainer.classList.add('show');
    bar.style.width = "0%";
    percent.textContent = "0%";
    msg.innerHTML = "";

    const data = new FormData();
    data.append("file", file);

    /* Fake progress */
    let p = 0;
    const timer = setInterval(() => {
        p += Math.random() * 8;
        if (p < 90) {
            bar.style.width = p + "%";
            percent.textContent = Math.round(p) + "%";
        }
    }, 400);

    try {
        const r = await fetch("/upload", {
            method: "POST",
            body: data
        });

        const j = await r.json();

        clearInterval(timer);
        bar.style.width = "100%";
        percent.textContent = "100%";

        setTimeout(() => {
            progContainer.classList.remove('show');
            msg.innerHTML = `
                <div class="success-icon">✅</div>
                <div style="margin-bottom:5px;font-weight:600;">Reduction Complete!</div>
                <a href="/download/${j.file}">
                    <i class="fa-solid fa-download"></i>
                    Download Result
                </a>
            `;
        }, 500);

    } catch {
        clearInterval(timer);
        msg.innerHTML = '<span style="color:#f87171">❌ Failed. Please try again.</span>';
        progContainer.classList.remove('show');
    }

    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-compress"></i> Reduce Video';
};

</script>

</body>
</html>
"""


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    uid = str(uuid.uuid4())
    name = uid + "_" + file.filename
    in_path = os.path.join(UPLOAD, name)

    with open(in_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    subprocess.run([
        sys.executable,
        "video_reducer.py",
        in_path
    ])

    out_path = in_path.replace(".mp4", "_reduced.mp4")
    final = os.path.join(OUTPUT, os.path.basename(out_path))
    shutil.move(out_path, final)

    return {"file": os.path.basename(final)}


@app.get("/download/{f}")
def download(f: str):
    path = os.path.join(OUTPUT, f)
    return FileResponse(path, filename=f)
