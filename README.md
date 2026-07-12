
<div align="center">
  
  # 🌐 Browser API
  
  **A CLI that bridges your browser's Gemini session to a local OpenAI-compatible API, no API key required.**
  
  Read about it at: www.muhammetozmen.org/projects/project-browserAPI/
  
  [![GitHub Stars](https://img.shields.io/github/stars/muhammetozmen/browserAPI?style=for-the-badge&logo=github&color=FFDD00&labelColor=202020)](https://github.com/muhammetozmen/browserAPI/stargazers)
  [![GitHub Forks](https://img.shields.io/github/forks/muhammetozmen/browserAPI?style=for-the-badge&logo=git&color=FF69B4&labelColor=202020)](https://github.com/muhammetozmen/browserAPI/network/members)
  [![GitHub License](https://img.shields.io/github/license/muhammetozmen/browserAPI?style=for-the-badge&logo=law&color=00C9FF&labelColor=202020)](https://github.com/muhammetozmen/browserAPI/blob/main/LICENSE)

  <br/>
  
  > **If you find this project useful, please consider giving it a ⭐ on GitHub!** <br> 
  > *Your support helps keep this project alive and updated.*

</div>

---
## [!] LEGAL NOTICE
**This tool is an independent, unofficial project developed strictly for educational, research, and personal testing purposes, and is in no way affiliated with, authorized by, or endorsed by Google LLC. Because it interacts with unofficial APIs, its use may directly violate Google’s Terms of Service and could result in severe consequences, including temporary or permanent account bans, rate limits, or data loss. The software is provided "as is" without any warranties of any kind, and under no circumstances shall the author be held liable for any direct, indirect, incidental, or consequential damages, financial losses, or legal actions resulting from its use. By choosing to download, install, or use this tool, you acknowledge that you do so entirely at your own risk and accept full responsibility for your actions, including compliance with all applicable platform terms and local laws.**

---
## Requirements

- python 3.11+ (I highly suggest 3.11)
- pip package manager
- venv module
## Installation

There is nothing fancy with installation process, you can directly download project and use it. I can create a package or script in next updates, for now, stick with launching.

1. Clone project to your system and go to folder.
```bash
git clone https://github.com/muhammetozmen/browserAPI.git
cd browserAPI
```

2. You can install venv and modules with `install.sh` on *linux/mac* or `install.bat` on *windows*.

***Alternatively*** you can install with this two commands:
```bash
python3 -m venv .venv # For linux and mac
python -m venv .venv # For windows
.venv/bin/pip install -r requirements.txt # For linux and mac
.venv\Scripts\pip install -r requirements.txt # For windows
```

3. Launch the CLI via `lin_run.sh`, `mac_run.sh` or `win_run.bat` like this.
```bash
./lin_run.sh # For linux
./mac_run.sh # For mac
./win_run.bat # For windows
```

***Alternatively*** you can run app with:
```bash
.venv/bin/python3 src/main.py #For linux and mac
.venv/Scripts/python src/main.py #For windows
```

That's all. CLI should be launched now.
## Usage

### First Usage
After setting the language and accepting the legal disclaimer and user consent, you will get the "FIRST-TIME INITIALIZATION: SELECT DEFAULT BROWSER" settings. Pick your browser that has been logged in with a Gemini account. It doesn't have to be a plus/pro/ultra account to be used, but your limits will still be affected by your plan.

If it can't find your browser path automatically, you have to enter it manually. 
You can share your path with me there, so I can include it in the next update: https://github.com/muhammetozmen/browserAPI/issues/1

You can change the host address to something else. If you are going to use it locally, you can just press Enter to set it to the default address. The same goes for the host.
You can change your models. There will be three models to select: the weak, default, and pro model. I included this system for the next updates that might add new models, so you can limit your model numbers and use only certain models with this API. For now, you can just press Enter and select what's picked by default.
You can change your log saves and cookie refresh intervals too. I don't suggest doing that.

After getting "INITIALIZATION SUCCESSFUL!", you can press Enter and use it.
### General Usage
After setting config file, you will get MAIN MENU when you launch app. You can directly press "Start Local API Server (Default)" and launch the server. The other options are clear about what they do.

You can connect the browserAPI gateway directly to Open WebUI, Cursor, or Continuity to use it as a custom AI backend. You have options to integrate it:
#### Option A: Unified Connection (Single Base URL)
Add a single connection to route all models dynamically based on the model ID you select:
* **API URL**: `http://127.0.0.1:4747/v1`
* **API Key**: `anything` (a dummy key is required, but the local gateway ignores it)
* **Model Choices**: Select `gemini-2.0-flash` (default), `gemini-1.5-pro` (strong), or `gemini-2.0-flash-lite` (weak).

#### Option B: Model-Specific Connections (Separate Base URLs)
If your application requests separate connections or Base URLs for different tasks (e.g., using a fast, weak model for inline autocomplete, and a strong model for complex chats/reasoning), you can register multiple connections:

1. **Connection 1 (Forces Default Model)**:
   * **API URL**: `http://127.0.0.1:4747/v1/default`
   * **API Key**: `anything`
2. **Connection 2 (Forces Strong Model)**:
   * **API URL**: `http://127.0.0.1:4747/v1/strong`
   * **API Key**: `anything`
3. **Connection 3 (Forces Weak Model - Autocomplete)**:
   * **API URL**: `http://127.0.0.1:4747/v1/weak`
   * **API Key**: `anything`
