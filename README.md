# ADB Helper

This project provides an easy-to-use PowerShell script that interacts with Android Debug Bridge (ADB) to manage and control Android devices. The script includes various commands to simplify tasks like installing/uninstalling APKs, managing device connections, and rebooting Android devices. It is provided in two versions: as a script and as a converted executable with the normal presetted script path (.exe).

## Features

The script supports the following commands:

- **Connection Commands:**
  - `-c` - Connect to device via IP
  - `-d` - Disconnect device via IP
  - `-t` - Restart ADB in TCP/IP mode on device

- **ADB Server Control:**
  - `-ss` - Start the ADB server
  - `-ks` - Kill the ADB server

- **Device Management:**
  - `-r` - Reboot Device (Normal)
  - `-rb` - Reboot into Bootloader
  - `-rr` - Reboot into Recovery
  - `-root` - Restart ADB daemon with root permissions
  - `-re-m` - Remount System Partition (requires root)

- **Package Management:**
  - `-i` - Install APK
  - `-u` - Uninstall APK (by package name)
  - `-da` - Disable App (by package name)
  - `-e` - Enable App (by package name)
  - `-lp` - List Installed Packages
  - `-lpl` - List Packages with File Locations

- **File Management:**
  - `-pft` - Push File (PC -> Device)
  - `-ptf` - Pull File (Device -> PC)

- **Additional Commands:**
  - `-lc` - Output device Logcat
  - `-av` - Show ADB Version
  - `help` - Shows help menu with command descriptions
  - `clear` - Clears the screen
  - `exit` - Exits the script

## Requirements

- **Windows Operating System**
- **PowerShell** (for the script version)
- **ADB (Android Debug Bridge)** must be installed and accessible in your system's PATH. The script will attempt to locate ADB in the following locations:
  1. ADB in your system's PATH
  2. Default Android SDK location (`%LOCALAPPDATA%\Android\Sdk\platform-tools`)
  3. A fallback location (`C:\Users\<username>\AppData\Local\Android\Sdk\platform-tools`)

If ADB is not found, the script will notify you to install it or update the fallback path.

## Usage

### Script Version

1. **Download the Script**:  
   Clone or download the repository.
   
2. **Run the Script**:  
   Open PowerShell and run the script.

3. **Execute Commands**:  
   Once the script is running, you can input commands interactively. Type `help` to see available commands.

4. **Exit**:  
   Type `exit` to stop the script.

### Executable Version

1. **Download the Executable**:  
   Download the `.exe` file from the releases section.

2. **Run the Executable**:  
   Double-click the executable to launch the application.

3. **Execute Commands**:  
   The executable works similarly to the script version, but it is packaged into a single file for ease of use.

## Configuration

The script attempts to detect the path to `adb.exe` automatically. If ADB is not in the system's PATH, it will try the default SDK location and a fallback directory. If ADB is still not found, the script will display an error message and prompt you to exit.

### Customizing ADB Path

If needed, you can manually specify the path to `adb.exe` by updating the fallback path in the script:
```powershell
$fallbackPath = "C:\Path\To\Your\SDK\platform-tools"
