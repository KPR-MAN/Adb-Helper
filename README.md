# Adb Helper (GUI) 🎨 & Adb Helper (Script)

A user-friendly graphical interface (`Adb Helper (GUI)`) and a command-line script (`Adb Helper (Script)`) for executing common Android Debug Bridge (adb) commands, simplifying interactions with Android devices 📱.

**Repository:** [https://github.com/KPR-MAN/Adb-Helper](https://github.com/KPR-MAN/Adb-Helper)  KPR-MAN/Adb-Helper

## GUI ✨🖼️
![image](https://github.com/user-attachments/assets/585357aa-77d5-4d87-a030-d7ac5e9774bc)

## Script ⌨️
![image](https://github.com/user-attachments/assets/e2c8213b-7c6f-4741-b5b8-217ce9d59ec2)


## Description 📝

This repository provides two tools for interacting with Android devices via ADB:

1.  **`Adb Helper (GUI)` 🎨🐍:** A graphical application built with Python and Tkinter (`ttk` themed widgets). It offers a visual way to run ADB commands through buttons and input fields, displaying output directly within the application.
2.  **`Adb Helper (Script)` ⌨️:** The original PowerShell command-line script providing similar functionality within a terminal environment.

Both tools automatically attempt to detect the ADB installation path 🔍.

## ✨ Features ✨

*   ✅ **Automatic ADB Detection:** Attempts to find `adb.exe` (or `adb`) in the system's PATH, default Android SDK locations, or a fallback path.
*   ✅ **Connection Management:** Connect/disconnect via IP, set TCP/IP mode.
*   ✅ **ADB Server Control:** Start/kill the ADB server.
*   ✅ **Device Information:** Show ADB version, list installed packages (with or without paths).
*   ✅ **Device Interaction:** Start ADB shell (attempts to open in a new console), reboot (Normal, Bootloader, Recovery).
*   ✅ **File Management:** Push/pull files using system file/folder selection dialogs 📥📤.
*   ✅ **Application Management:** Install APKs (via file dialog), uninstall/disable/enable apps by package name 📦.
*   ✅ **Debugging & Advanced:** ADB root, remount system partition, stream `logcat` into the GUI 📊, stop `logcat` stream 🛑.
*   ✅ **Interface:** Clear button layout, dedicated input fields, scrollable/color-coded output area, built-in help 💡, dark theme 🌙.

*   ⚠️ Some features aren't available in script version...

## ⚙️ Requirements (For GUI Version) ⚙️
*(The Script only requires ADB installed and accessible)*

1.  🐍 **Python 3.x:** Required for `Adb Helper (GUI)`. Download from [python.org](https://www.python.org/).
2.  🎨 **Tkinter:** Required for `Adb Helper (GUI)`. Usually included with Python. On some Linux systems, it may need separate installation (e.g., `sudo apt-get update && sudo apt-get install python3-tk`).
3.  ⌨️ **PowerShell:** Required for `Adb Helper (Script)`. Included with modern Windows versions.
4.  🤖 **Android Debug Bridge (ADB):**
    *   Required for both tools ✅. Part of the Android SDK Platform Tools. Download from [developer.android.com](https://developer.android.com/studio/releases/platform-tools).
    *   Ensure the `platform-tools` directory containing `adb` is added to the system's **PATH** environment variable 🌐 for reliable detection, or that ADB resides in a standard SDK location.
    *   Verify the ADB installation by opening a terminal/command prompt and running `adb version` ➡️💻.

## 🚀 Installation 🚀

1.  Ensure all **Requirements** are met ✅.
2.  📦 Clone the repository:
    ```bash
    git clone https://github.com/KPR-MAN/Adb-Helper.git
    cd Adb-Helper
    ```
3.  No additional Python package installations are required for the current GUI version 👍.

Or download the file directly...

## ▶️ Usage ▶️

### Adb Helper (GUI) 🎨

1.  Navigate to the repository directory in a file explorer 📁.
2.  Click on the python file `Adb Helper (GUI)` 🖱️.
3.  Follow the GUI for how to use... 👉

### Adb Helper (Script)

1.  Navigate to the repository directory in a file explorer 📁.
2.  Right Click on the script file `Adb Helper (Script)` 🖱️.
3.  Select `Run With PowerShell` in the right click menu ✅.
4.  Follow the prompts within the terminal. Type `help` for available commands within the script's interface... 💡

## 📌 Notes 📌

*   If ADB is not found automatically ❓, ensure it is correctly installed and accessible via the system's PATH ⚠️.
*   The "Start Shell" feature in the GUI attempts to launch a new external terminal window 💻.
*   The `logcat` command streams output continuously 📊 until stopped via the "Stop Logcat" button (GUI) 🛑 or Ctrl+C (Script, typically).
