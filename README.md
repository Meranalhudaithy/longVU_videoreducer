# 🎬 LongVU Video Reducer

**LongVU Video Reducer** is a lightweight, local-first tool for reducing video size and visual redundancy, making videos more efficient for **AI models, storage, and preprocessing pipelines**.

It focuses on **video token reduction** — not training or inference.

---

## ✨ Features

LongVU optimizes videos by:

* ⏱ Sampling fewer frames per second
* 🧠 Removing visually similar frames
* 📉 Adaptively reducing spatial resolution
* 📦 Producing compact MP4 files with minimal semantic loss

Ideal for:

* Vision–Language Models (VLMs)
* Video-to-text pipelines
* Dataset preparation
* Storage optimization

---

## 🚫 Limitations

LongVU does **not** provide:

* ❌ LLM inference
* ❌ Model training
* ❌ Cloud services
* ❌ GPU dependency

All processing runs **locally** using Python and OpenCV.

---

## 🖥️ Web Interface

The project includes a simple local web interface built with **FastAPI**:

* Drag & drop video uploads
* One-click reduction
* Download optimized results

Runs locally at:

```
http://127.0.0.1:8000
```

---

## ⚙️ Installation

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

### 2. Activate the Environment

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install fastapi uvicorn opencv-python python-multipart pillow imagehash numpy
```

---

## ▶️ Running the App

From the project root directory:

```bash
python -m uvicorn web_app:app --reload
```

Then open your browser:

```
http://127.0.0.1:8000
```

---

## 📁 Project Structure

```
LongVU/
│
├── web_app.py         # FastAPI web interface
├── video_reducer.py  # Core reduction logic
├── uploads/           # Temporary uploaded videos
├── outputs/           # Reduced output videos
├── requirements.txt   # Dependencies
└── README.md          # Documentation
```

---

## 🧪 Example: Before vs After

### 🎥 Original Video

* File: `videos\dia130_utt11 1.mp4`
* Size: ~649 KB

### 🎯 Reduced Output

* File: `videos\c68e0901-3b97-4efd-8e7a-4163e1401ff4_dia130_utt11 1_reduced.mp4`
* Size: ~278 KB
* Reduction: ~57%

---

## 📊 Size Comparison

| Version  | Size   |
| -------- | ------ |
| Original | 649 KB |
| Reduced  | 278 KB |
| Savings  | ~57%   |

---

## 🧠 Why This Matters for AI

Video models do not process files — they process **tokens**.

By reducing:

* Frame count
* Visual redundancy
* Unnecessary spatial detail

You can:

* Lower compute costs
* Accelerate preprocessing pipelines
* Improve scalability
* Reduce dataset storage requirements

---

## 🚀 Roadmap & Future Improvements

Planned enhancements include:

* Batch video processing
* CLI support with quality presets
* Keyframe-only export mode
* Dataset-aware optimization
* Optional audio stripping
* Preset profiles for different model types

---

## 📜 License

This project is licensed under the **MIT License**.

---

## ✨ Credits

Built using:

* Python
* OpenCV
* FastAPI
* NumPy
* ImageHash

Designed for efficient, local-first video optimization in AI pipelines.
