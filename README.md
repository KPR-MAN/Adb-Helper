# Adb Helper (GUI) & Adb Helper (Script)

A user-friendly graphical interface (`Adb Helper (GUI)`) and a command-line script (`Adb Helper (Script)`) for executing common Android Debug Bridge (adb) commands, simplifying interactions with Android devices.

**Repository:** [https://github.com/KPR-MAN/Adb-Helper](https://github.com/KPR-MAN/Adb-Helper)

## GUI ![image](https://github.com/user-attachments/assets/585357aa-77d5-4d87-a030-d7ac5e9774bc)

## Script ![image](https://github.com/user-attachments/assets/e2c8213b-7c6f-4741-b5b8-217ce9d59ec2)


## Description

This repository provides two tools for interacting with Android devices via ADB:

1.  **`Adb Helper (GUI)`:** A graphical application built with Python and Tkinter (`ttk` themed widgets). It offers a visual way to run ADB commands through buttons and input fields, displaying output directly within the application.
2.  **`Adb Helper (Script)`:** The original PowerShell command-line script providing similar functionality within a terminal environment.

Both tools automatically attempt to detect the ADB installation path.

## Features

*   **Automatic ADB Detection:** Attempts to find `adb.exe` (or `adb`) in the system's PATH, default Android SDK locations, or a fallback path.
*   **Connection Management:** Connect/disconnect via IP, set TCP/IP mode.
*   **ADB Server Control:** Start/kill the ADB server.
*   **Device Information:** Show ADB version, list installed packages (with or without paths).
*   **Device Interaction:** Start ADB shell (attempts to open in a new console), reboot (Normal, Bootloader, Recovery).
*   **File Management:** Push/pull files using system file/folder selection dialogs.
*   **Application Management:** Install APKs (via file dialog), uninstall/disable/enable apps by package name.
*   **Debugging & Advanced:** ADB root, remount system partition, stream `logcat` into the GUI, stop `logcat` stream.
*   **Interface:** Clear button layout, dedicated input fields, scrollable/color-coded output area, built-in help, dark theme.

## Requirements (For GUI Version) - The Script Does Not Require anything unless the adb

1.  **Python 3.x:** Required for `Adb Helper (GUI)`. Download from [python.org](https://www.python.org/).
2.  **Tkinter:** Required for `Adb Helper (GUI)`. Usually included with Python. On some Linux systems, it may need separate installation (e.g., `sudo apt-get update && sudo apt-get install python3-tk`).
3.  **PowerShell:** Required for `Adb Helper (Script)`. Included with modern Windows versions.
4.  **Android Debug Bridge (ADB):**
    *   Required for both tools. Part of the Android SDK Platform Tools. Download from [developer.android.com](https://developer.android.com/studio/releases/platform-tools).
    *   Ensure the `platform-tools` directory containing `adb` is added to the system's **PATH** environment variable for reliable detection, or that ADB resides in a standard SDK location.
    *   Verify the ADB installation by opening a terminal/command prompt and running `adb version`.
    *   

## Installation

1.  Ensure all **Requirements** are met.
2.  Clone the repository:
    ```bash
    git clone https://github.com/KPR-MAN/Adb-Helper.git
    cd Adb-Helper
    ```
3.  No additional Python package installations are required for the current GUI version.

## Usage

### Adb Helper (GUI)

1.  Navigate to the repository directory in a terminal or command prompt.
2.  Run the Python script (assuming the Python script file is named `adb_helper_gui.py` - adjust if necessary):
    ```bash
    python adb_helper_gui.py
    ```
    (Use `python3` if required by the system configuration).
3.  The `Adb Helper (GUI)` window will open.
4.  Use the input fields for required information (IP, Port, Package Name, etc.).
5.  Click the button corresponding to the desired ADB command.
6.  Observe results and status messages in the output text area.

### Adb Helper (Script)

1.  Open a PowerShell terminal.
2.  Navigate to the repository directory.
3.  Run the script (assuming the PowerShell script file is named `Adb Helper (Script).ps1` - adjust if necessary):
    ```powershell
    .\'Adb Helper (Script).ps1'
    ```
4.  Follow the prompts within the terminal. Type `help` for available commands within the script's interface.

## Notes

*   If ADB is not found automatically, ensure it is correctly installed and accessible via the system's PATH.
*   The "Start Shell" feature in the GUI attempts to launch a new external terminal window.
*   The `logcat` command streams output continuously until stopped via the "Stop Logcat" button (GUI) or Ctrl+C (Script, typically).
