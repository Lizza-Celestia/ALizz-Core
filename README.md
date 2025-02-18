# ALizz-Core

**ALizz-Core** is a modular Python framework that allows running multiple Python scripts as plugins. Communication between plugins is handled via a **subscriber/publisher event bus**. 

Ready-made plugins are available at [ALizz-Plugins](https://github.com/Lizza-Celestia/ALizz-Plugins).

This project was originally developed as a **modular and flexible general AI assistant**, but it can be adapted for various use cases.

## How ALizz-Core Works

Each component of an AI assistant is implemented as a plugin:

- **Speech-to-Text (STT)** is a plugin
- **Text-to-Speech (TTS)** is a plugin
- **Language Model (LLM)** is a plugin
- **Discord bot** is a plugin
- Any custom function can be implemented as a plugin

Plugins function as **independent black boxes** with defined inputs and outputs, enabling standardized communication between them. Plugins are **not dependent on each other** and can run in any configuration as long as their input (subscriptions) and output (publishing) match.

### Example: STT to TTS
- **STT Plugin**: Takes microphone input and publishes a transcript.
- **TTS Plugin**: Subscribes to the STT output, processes the text, and plays it through speakers.

---

## 📖 Table of Contents 
- [Installation](#installation)
    - [Windows](#windows-installation-using-vs-code)
- [Troubleshooting](#troubleshooting)
- [Plugins](#plugins)
    - [Custom Plugins](#custom-plugins)
- [Inspiration & Credits](#inspiration--credits)

---

## 🔧 Installation
### Windows Installation Using VS Code

1. **Install Python** (Recommended: Python 3.10.10)
2. **Install VS Code** and the **Python extension**
3. **Open the project folder** in VS Code
4. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv_ALizz_Core
   .\venv_ALizz_Core\Scripts\activate
   python -m pip install --upgrade pip
   ```
5. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
6. **Run the main script:**
   ```bash
   python main.py
   ```

<!-- > **Note:** Linux installation instructions will be added later. -->

---

## ⚠️ Troubleshooting

### 1. First-time Run Errors
If an error occurs when running the code for the first time, follow these steps:

- Open **PowerShell** and enter the following command:
  ```powershell
  Set-ExecutionPolicy Unrestricted -Scope CurrentUser
  ```
- Alternatively, for all users:
  ```powershell
  Set-ExecutionPolicy Unrestricted -Scope LocalMachine
  ```

### 2. Run Code Not Working in VS Code
- Ensure the terminal **shows the project's root path**.
- Verify that the **virtual environment is activated**.
- Try running the script again.

---

## 🧩 Plugins

### 🔹 Ready-made Plugins
Find ready-made plugins at: [ALizz-Plugins](https://github.com/Lizza-Celestia/ALizz-Plugins)

### 🔹 Custom Plugins
Use `sample_plugin.py` as a reference to create your own custom plugins.

#### 🔹 Plugin Naming Conventions (Case Sensitive)
| Component       | Naming Convention |
|----------------|------------------|
| **Folder Name** | `plugin_name` |
| **Script Name** | `plugin_name_plugin.py` |
| **Class Name** | `class Plugin_namePlugin(BasePlugin)` |
| **Constructor** | `def __init__(self, core, enabled=True):` |

Example `__init__` function:
```python
def __init__(self, core, enabled=True):
    self.core = core  # Enables the event bus for pub/sub events
```

#### 🔹 Enabling Plugins Automatically
An empty `__init__.py` file **must** be placed inside the plugin folder:
```
./plugins/plugin_name/__init__.py
```

---

## 🌟 Inspiration & Credits

This is my first project using Python to develop a **modular AI assistant**. It took multiple iterations and concept refinements before reaching a design that I was happy with.

- **Project Started:** Mid-December 2024
- **First Working Version:** Mid-February 2025

While working on this, I took inspiration from:
- **[Neuro-sama second annual subathon (2024-2025)](https://www.youtube.com/@Neurosama)**
- **[Neuro](https://github.com/kimjammer/Neuro)**
---
