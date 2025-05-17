# 🎤 D33P-SP34K CLI Tool

 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Python Versions](https://img.shields.io/pypi/pyversions/deepgram-sdk)]()

```
    ██████  ██████  ██████  ██████        ███████ ██████  ██████  ██   ██ ██   ██ 
    ██   ██      ██      ██ ██   ██       ██      ██   ██      ██ ██   ██ ██  ██  
    ██   ██  █████   █████  ██████  █████ ███████ ██████   █████  ███████ █████   
    ██   ██      ██      ██ ██                 ██ ██           ██      ██ ██  ██  
    ██████  ██████  ██████  ██            ███████ ██      ██████       ██ ██   ██ 
     
```

A CLI for transcribing audio/video files with Deepgram’s Speech-to-Text API. Includes auto video→audio extraction, smart formatting, punctuation, paragraphs, utterances (speaker diarization), automatic chunking, logging, progress bars, and more!

---

## 📑 Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)

   * [Basic](#basic)
   * [Advanced Options](#advanced-options)
6. [Examples](#examples)
7. [How It Works](#how-it-works)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)
10. [Resources](#resources)
11. [Contributing](#contributing)
12. [Changelog](#changelog)

---

## 🚀 Features

* **Single-request** for files ≤ 2 GB (no chunking)
* **Auto video extraction**: convert common video formats (MP4, MOV, MKV, AVI) to WAV
* **Chunking** for files > 2 GB with configurable chunk size
* **Utterances**: optional speaker diarization and timestamps
* **Smart formatting** for currencies, dates, emails, and more
* **Punctuation** and **paragraphs** by default
* **Multiple models**: `nova-2`, `nova-3`, `whisper`
* **Live progress bars** via `tqdm`
* **Detailed logging** using Python’s `logging` module

---

## 📋 Prerequisites

1. **Python 3.8+**
2. **ffmpeg** in PATH:

   * **Linux**: `sudo apt-get install -y ffmpeg`
   * **macOS**: `brew install ffmpeg`
   * **Windows**: download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to `%PATH%`
3. A **Deepgram API key** (free sign-up at [https://deepgram.com](https://deepgram.com))

---

## ⚙️ Installation

```bash
# Clone repository or download script
# Install dependencies
pip install python-dotenv pydub deepgram-sdk tqdm
```

---

## 🔧 Configuration

Create a `.env` file in the script directory:

```dotenv
DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

Alternatively, you can export the key in your shell:

```bash
export DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

---

## 🏁 Usage

```bash
python transcribe.py --file INPUT_FILE [options]
```

### 🔹 Basic

```bash
python transcribe.py -f speech.wav -o transcript.txt
```

### 🔹 Advanced Options

| Flag             | Type    | Default  | Description                               |
| ---------------- | ------- | -------- | ----------------------------------------- |
| `-f`, `--file`   | string  | **Req**  | Path to audio/video file                  |
| `--model`        | string  | `nova-2` | Model: `nova-2`, `nova-3`, or `whisper`   |
| `--language`     | string  | `it`     | ISO language code (e.g. `en`, `it`, `es`) |
| `--utterances`   | boolean | `False`  | Include speaker diarization & timestamps  |
| `--chunk-length` | int     | `10`     | Chunk length (minutes) for files > 2 GB   |
| `-o`, `--output` | string  | STDOUT   | Output transcript file                    |

---

## 🔍 Examples

### 1. Italian transcript (default)

```bash
python transcribe.py -f lecture.mp3 -o lecture-it.txt
```

### 2. English transcript with utterances

```bash
python transcribe.py --file podcast.mp3 --language en --utterances \
                       --output podcast_en.txt
```

### 3. Auto-extract & chunk a large video

```bash
python transcribe.py -f webinar.mkv --chunk-length 5 -o webinar.txt
```

### 4. Print to console

```bash
python transcribe.py -f interview.wav
```

---

## ⚙️ How It Works

1. **Load API key** via `python-dotenv`.
2. **Display banner** and **initialize logging**.
3. **Validate input** path and extension.
4. **Video detection**: extract audio if needed.
5. **Size check**:

   * **≤ 2 GB**: `transcribe_whole` uploads file directly.
   * **> 2 GB**: `transcribe_chunks` splits audio via `pydub.make_chunks`.
6. **Deepgram transcription** via `deepgram.listen.rest.v('1').transcribe_file(...)`.
7. **Post-process**: replace literal `\n` with real newlines.
8. **Output**: write to file or STDOUT.

---

## 🛠️ Troubleshooting

* **`PermissionError` on Windows**: ensure temp files are closed before deletion.
* **Timeouts**: check network stability; consider chunking smaller segments.
* **Unsupported format**: convert your file with ffmpeg: `ffmpeg -i input.xyz output.wav`.

---

## ❓ FAQ

**Q:** Can I transcribe real-time streaming?
**A:** This tool is for pre-recorded files. See Deepgram’s [live streaming guide](https://docs.deepgram.com/docs/live-streaming). *But maybe in the next version :)*

**Q:** How do I handle long audio?
**A:** Use `--chunk-length` to adjust segment duration; default is 10 min.

**Q:** Can I change log level?
**A:** Adjust `logging.basicConfig(level=logging.DEBUG)` in code.

---

## 📚 Resources

* **Deepgram API Playground**: [https://playground.deepgram.com/?endpoint=listen](https://playground.deepgram.com/?endpoint=listen)
* **SDK Documentation**: [https://github.com/deepgram/deepgram-python-sdk](https://github.com/deepgram/deepgram-python-sdk)
* **Supported Formats**: [https://docs.deepgram.com/docs/supported-audio-formats](https://docs.deepgram.com/docs/supported-audio-formats)
* **API Limits**: [https://docs.deepgram.com/reference/api-rate-limits](https://docs.deepgram.com/reference/api-rate-limits)

---

## 🤝 Contributing

Contributions welcome! Please open issues or pull requests. Ensure code style consistency and update this README.

---

## 📝 Changelog

* **v1.0.0** – Initial release with basic transcription and chunking.
* **v1.1.0** – Added utterances, logging, and progress bars.
* **v1.2.0** – Auto video→audio, improved error handling.
* **v1.3.0** – Fixed chunking process.
* **v1.3.1** – Enhanced README, added FAQ and badges.


*Happy transcribing!* 🚀
