<p align="center">
  <img src="https://raw.githubusercontent.com/d4rkvista/MorpheusDL/main/icon.png" alt="MorpheusDL Logo" width="120" />
</p>

<h1 align="center">MorpheusDL</h1>
<p align="center">⚡ Next-Gen Media Downloader powered by yt-dlp and PyQt ⚡</p>

<p align="center">
  <a href="https://github.com/d4rkvista/MorpheusDL/stargazers"><img src="https://img.shields.io/github/stars/d4rkvista/MorpheusDL?style=flat-square" /></a>
  <a href="https://github.com/d4rkvista/MorpheusDL/blob/main/LICENSE"><img src="https://img.shields.io/github/license/d4rkvista/MorpheusDL?style=flat-square" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg?style=flat-square" /></a>
  <a href="https://github.com/d4rkvista/MorpheusDL/commits/main"><img src="https://img.shields.io/github/last-commit/d4rkvista/MorpheusDL?style=flat-square" /></a>
</p>

---

## ✨ Features
- Fast, multithreaded downloads (optimized thread pool handling)
- Supports both video and audio downloads
- Automatic metadata + thumbnails embedding
- JSON-based customizable settings
- User-friendly GUI
- Smooth thumbnail previews with durations

---

## 🚀 Installation
```bash
# Clone the repository
git clone https://github.com/d4rkvista/MorpheusDL.git

# Enter the project directory
cd MorpheusDL

# Install dependencies
pip install -r requirements.txt

# Run the program
python MDL.py
# or just double-click 'MDL.py' file
```
# Installing aria2c

Your system must have aria2c installed for MorpheusDL to work properly.

# 🔹 Windows
## Method 1: Using winget (recommended)

Open CMD or PowerShell (as Administrator).

Run:
```bash
#installation
winget install aria2

#verify
aria2c -v
```
## Method 2: Manual Installation

Download the latest Windows build from:
👉 <a href=https://github.com/aria2/aria2/releases> aria2 Releases (GitHub) </a>

Look for ` aria2-<version>-win-64bit-build1.zip `

Extract the `.zip` file.

Move the `aria2c.exe` file to a folder of your choice.
(Recommended: `C:\Program Files\aria2c\`)

Add the folder to your <b>System PATH</b>:

Press `Win + R`, type `sysdm.cpl`, and hit Enter.

Go to <b>Advanced</b> → <b>Environment Variables.</b>

Under <b>System variables</b>, find and edit <b>Path</b>.

Add the folder path (e.g., `C:\Program Files\aria2c\`).

Click <b>OK</b> and restart your terminal.

Test installation:
```bash
#verify
aria2c -v
```
# 🔹 Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install aria2 -y
```

Verify:
```bash
aria2c -v
```
# 🔹 Linux (Arch/Manjaro)
```bash
sudo pacman -S aria2
```
Verify:
```bash
aria2c -v
```

# 🔹 macOS (Homebrew)

Install Homebrew if you don’t have it:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install aria2:
```bash
brew install aria2
```

Verify:
```bash
aria2c -v
```
✅ Once installed, MorpheusDL will automatically detect and use aria2c.
---

# Installing ffmpeg

Your system must have ffmpeg installed for MorpheusDL to merge video/audio streams and extract audio formats (e.g. MP3).

# 🔹 Windows
## Method 1: Using winget (recommended)

Open CMD or PowerShell (as Administrator).

Run:
```bash
#installation
winget install --id Gyan.FFmpeg

#verify
ffmpeg -version
```
## Method 2: Manual Installation

Download the latest Windows build from:
👉 <a href=https://www.gyan.dev/ffmpeg/builds/> ffmpeg Builds (Gyan.dev) </a>

Look for the `release essentials` build.

Extract the `.zip` file.

Move the extracted folder to a location of your choice.
(Recommended: `C:\Program Files\ffmpeg\`)

Add the `bin` folder to your <b>System PATH</b>:

Press `Win + R`, type `sysdm.cpl`, and hit Enter.

Go to <b>Advanced</b> → <b>Environment Variables.</b>

Under <b>System variables</b>, find and edit <b>Path</b>.

Add the folder path (e.g., `C:\Program Files\ffmpeg\bin`).

Click <b>OK</b> and restart your terminal.

Test installation:
```bash
#verify
ffmpeg -version
```
# 🔹 Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install ffmpeg -y
```

Verify:
```bash
ffmpeg -version
```
# 🔹 Linux (Arch/Manjaro)
```bash
sudo pacman -S ffmpeg
```
Verify:
```bash
ffmpeg -version
```

# 🔹 macOS (Homebrew)

Install Homebrew if you don't have it:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install ffmpeg:
```bash
brew install ffmpeg
```

Verify:
```bash
ffmpeg -version
```
✅ Once installed, MorpheusDL will automatically detect and use ffmpeg.
---

# Installing Deno

Your system must have Deno installed for MorpheusDL to work properly.

# 🔹 Windows
## Method 1: Using winget (recommended)

Open CMD or PowerShell (as Administrator).

Run:
```bash
#installation
winget install DenoLand.Deno

#verify
deno --version
```
## Method 2: Manual Installation

Download the latest Windows build from:
👉 <a href=https://github.com/denoland/deno/releases> Deno Releases (GitHub) </a>

Look for `deno-x86_64-pc-windows-msvc.zip`

Extract the `.zip` file.

Move the `deno.exe` file to a folder of your choice.
(Recommended: `C:\Program Files\deno\`)

Add the folder to your <b>System PATH</b>:

Press `Win + R`, type `sysdm.cpl`, and hit Enter.

Go to <b>Advanced</b> → <b>Environment Variables.</b>

Under <b>System variables</b>, find and edit <b>Path</b>.

Add the folder path (e.g., `C:\Program Files\deno\`).

Click <b>OK</b> and restart your terminal.

Test installation:
```bash
#verify
deno --version
```
# 🔹 Linux / macOS (Shell script)
```bash
curl -fsSL https://deno.land/install.sh | sh
```

Verify:
```bash
deno --version
```
# 🔹 macOS (Homebrew)

Install Homebrew if you don't have it:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install Deno:
```bash
brew install deno
```

Verify:
```bash
deno --version
```
✅ Once installed, MorpheusDL will automatically detect and use Deno.

> 💡 Note: ffmpeg, aria2c, and Deno can all also be installed directly from their official websites if you prefer not to use a package manager or CLI installer:
> - ffmpeg: https://www.gyan.dev/ffmpeg/builds/
> - aria2c: https://aria2.github.io/
> - Deno: https://deno.com/
---
# 🛣 Roadmap

- User-friendly settings GUI under development 

- GPU acceleration (CUDA support)

- More output format options

- Dark/Light theme toggle

- Plugin system for more sites
---
# ⚡ Optimizations

- Uses thread pool sizing best practices for faster downloads

- Background thumbnail fetching avoids UI freezing

- Uses Aria2c as external downloading(can be disabled in 'settings.json')

- Configurable settings stored in JSON for flexibility. You can change settings in 'settings.json', but leaving non-integer and non-boolean  values as-is is highly recommended
---
# ❓ FAQ

### Q: I get HTTP Error 403: Forbidden

- A: Try updating yt-dlp or use cookies for restricted content.

### Q: Why is the GUI freezing?

- A: Make sure dependancies are upto-date and report local log to the devs.
---
# Acknowledgements

- yt-dlp for the backend

- PyQt5 for the GUI framework

- Aria2c for multi-threaded downloading and handling internet interuptions


---

## 📨 Feedback & Contribution
- 🐛 Found a bug or issue? [Open a Bug Report](https://github.com/d4rkvista/MorpheusDL/issues/new?labels=bug)
- 💡 Have a feature idea or improvement? [Request a Feature](https://github.com/d4rkvista/MorpheusDL/issues/new?labels=enhancement)
- 🔧 Want to contribute code? Check out the [Contributing Guidelines](CONTRIBUTING.md)