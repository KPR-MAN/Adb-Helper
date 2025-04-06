<p align="center">
  <img src="assets/icon.png" alt="Adb Helper Icon" width="128"/>
</p>

<h1 align="center">Adb Helper 📱✨</h1>

<p align="center">
  <strong>A User-Friendly GUI & Script for Android ADB Commands</strong>
</p>

<p align="center">
  <!-- Version Badge -->
  <a href="https://github.com/KPR-MAN/Adb-Helper/releases">
    <img src="https://img.shields.io/github/v/release/KPR-MAN/Adb-Helper?display_name=tag&sort=semver&logo=github" alt="Version 1.1">
  </a>
  <!-- License Badge -->
  <a href="https://www.gnu.org/licenses/gpl-3.0">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg?logo=gnu" alt="License: GPL v3">
  </a>
  <!-- Open Source Badge -->
  <a href="https://opensource.org/">
    <img src="https://img.shields.io/badge/Open_Source-%E2%9C%93-brightgreen?logo=opensourceinitiative" alt="Open Source">
  </a>
  <!-- GitHub Stars Badge -->
  <a href="https://github.com/KPR-MAN/Adb-Helper">
    <img src="https://img.shields.io/github/stars/KPR-MAN/Adb-Helper?style=social" alt="GitHub stars">
  </a>
  <!-- Python and PowerShell Badges -->
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python 3.x">
  <img src="https://img.shields.io/badge/PowerShell-Core-blueviolet?logo=powershell" alt="PowerShell Core Compatible">
</p>

<p align="center">
  Tired of typing repetitive <code>adb</code> commands? Need a simpler way to interact with your Android device? <br />
  <strong>Adb Helper</strong> offers both a Graphical Interface (GUI) and a Command-Line Script to streamline your ADB workflow!
</p>

## 🤔 Why Adb Helper?

*   🚀 **Boost Productivity:** Execute common ADB commands with a single click or simple input.
*   ✅ **Reduce Errors:** Avoid typos in complex commands.
*   🤩 **User-Friendly:** Choose between an intuitive GUI or a powerful script.
*   📊 **Visual Feedback:** See command output clearly (GUI) or directly in your terminal (Script).
*   🔍 **Smart ADB Detection:** Automatically finds your ADB installation in common locations.
*   💾 **Easy File Transfers:** Push/pull files and folders effortlessly.

---

## ✨ Features

Adb Helper provides two ways to simplify your ADB tasks:

**1. Adb Helper (GUI) 🎨 (Python/Tkinter)**
*   Visual interface with buttons for common tasks.
*   Real-time output display within the app.
*   File/folder selection using system dialogs.
*   Easy to use
*   Ideal for users who prefer a graphical workflow.

*   After opening press "Help" to know other features and know what you can do with the tool.

**2. Adb Helper (Script) ⌨️ (PowerShell)**
*   It do the same as the GUI version but with simple text.
*   Automates commands via simple text input.
*   Suitable for scripting and command-line users.

*   After opening write command "Help" to know other features and know what you can do with the tool.

**Core Functionality (Both Tools):**

*   🔗 **Connection:** Connect/disconnect via IP, enable TCP/IP.
*   🔌 **Server Control:** Start/kill the ADB server.
*   ℹ️ **Device Info:** Get ADB version, list devices, list packages.
*   🔄 **Reboot Options:** Normal, Bootloader, Recovery.
*   셸 **ADB Shell Access:** Quickly open a shell.
*   📂 **File Management:** Push/Pull files & folders.
*   📦 **App Management:** Install APKs, Uninstall, Enable/Disable apps.
*   🛠️ **Advanced:** `adb root`, `remount`, `logcat` streaming (with stop).

*(See the code or run the tools for the full list of specific commands!)*

---

## ✨ Sneak Peek

### Adb Helper (GUI) 🖼️
*A clean interface to manage your device visually.*
![GUI Screenshot](https://github.com/user-attachments/assets/2d599db7-8825-4b02-9b00-210cf728b1d3)

### Adb Helper (Script) ⌨️
*Control ADB directly from your PowerShell terminal.*
![Script Screenshot](https://github.com/user-attachments/assets/b7bd4e36-3d31-426e-a89e-5db43290563e)

---

## ⚙️ Requirements

**Essential for Both:**

1.  🤖 **Android Debug Bridge (ADB):**
    *   Download from the official [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools).
    *   **‼️ CRITICAL:** Add the `platform-tools` directory containing `adb.exe` (Windows) or `adb` (Linux/macOS) to your system's **`PATH`** environment variable.
    *   Verify by opening a *new* terminal/cmd and typing `adb version`. It should output the version number.

**Tool Specific:**

*   **For `Adb Helper (GUI)` 🎨🐍:**
    *   **Python 3.x:** Install from [python.org](https://www.python.org/). (Tkinter is usually included; install `python3-tk` on some Linux distros if needed).
*   **For `Adb Helper (Script)` ⌨️:**
    *   **PowerShell:** Included in modern Windows. Install [PowerShell Core](https://learn.microsoft.com/powershell/scripting/install/installing-powershell) for Linux/macOS.

---

## 🚀 Getting Started (Quick Start)

1.  **Install Requirements:** Make sure you have ADB (with PATH set!), and Python (for GUI) or PowerShell (for Script).
2.  **Get the Code:**
    ```bash
    # Clone the repository
    git clone https://github.com/KPR-MAN/Adb-Helper.git
    # Navigate into the directory
    cd Adb-Helper
    ```
    *(Alternatively, download and extract the ZIP from the GitHub page.)*
3.  **Ready to Run!** No extra Python packages (`pip install`) needed for the GUI.

---

## ▶️ How to Use

### Using the GUI 🎨

1.  Go to the `Adb-Helper` folder.
2.  Run the Python script:
    *   **Windows:** Double-click `Adb Helper (GUI).py` or run `python "Adb Helper (GUI).py"` in CMD/PowerShell.
    *   **Linux/macOS:** Run `python3 "Adb Helper (GUI).py"` in the terminal.
3.  Use the buttons and input fields. Output appears in the bottom text area.

### Using the Script ⌨️

1.  Go to the `Adb-Helper` folder.
2.  Open PowerShell in that directory (e.g., `Shift + Right-click` -> "Open PowerShell window here" on Windows).
3.  Execute the script:
    ```powershell
    .\Adb Helper (Script).ps1
    ```
    *(**Note:** You might need to adjust PowerShell's execution policy. Try `Set-ExecutionPolicy RemoteSigned -Scope Process` for the current session if you get an error. Be mindful of security implications.)*
4.  Follow the menu prompts. Type `help` for available commands within the script.

---

## 🤝 Contributing

**We welcome contributions!** Help make Adb Helper even better.

**Ways to Contribute:**

*   🐛 Report Bugs: Create an issue detailing the problem.
*   💡 Suggest Features: Open an issue to discuss new ideas.
*   ✨ Submit Pull Requests (PRs):
    1.  **Fork** the repository.
    2.  Create a new **Branch** (`git checkout -b feature/my-idea` or `fix/bug-name`).
    3.  Make your **Changes**.
    4.  **Test** thoroughly.
    5.  **Commit** with clear messages.
    6.  **Push** to your fork.
    7.  Open a **Pull Request** back to the main `KPR-MAN/Adb-Helper` repository.

**License Note:** By contributing, you agree that your contributions will be licensed under the project's GPLv3 License.

*Looking forward to your contributions!*

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.

You are free to Share and Adapt the code, provided you maintain Attribution and ShareAlike under the same license.

Visit the [gnu.org](https://www.gnu.org/licenses/gpl-3.0.html) for full details .

---

## 📌 Troubleshooting & Notes

*   **"ADB Not Found" Error:** This is common! **RE-CHECK** that the `platform-tools` folder is correctly added to your system `PATH`. **Restart** terminals or the GUI after updating the `PATH`. Test with `adb version` in a *new* terminal.
*   **PowerShell Script Execution Policy:** If the `.ps1` script won't run on Windows, see the note in the [How to Use](#user-content-using-the-script-%EF%B8%8F) section about `Set-ExecutionPolicy`. *(Self-correction: Need to update this link too)*
*   **GUI "Start Shell":** Tries to open `adb shell` in a new, separate terminal window. Behavior might vary by OS.
*   **Stopping `logcat`:** Use the "Stop Logcat" button (GUI) or press `Ctrl+C` (Script).
*   If the Gui can't open or crashes: Make sure the icon.png are in the assets folder.

---

<p align="center">Happy Coding! 🎉</p>
