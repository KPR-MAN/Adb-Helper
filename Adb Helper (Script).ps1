#region --- Configuration and ADB Path Detection ---

# Function to find ADB robustly
function Find-AdbPath {
    Write-Verbose "Attempting to find adb.exe..."
    # 1. Check PATH environment variable
    $adbExecutable = Get-Command adb.exe -ErrorAction SilentlyContinue
    if ($adbExecutable) {
        $adbPath = Split-Path $adbExecutable.Path -Parent
        Write-Host "[INFO] Found adb.exe in PATH: $adbPath" -ForegroundColor Cyan
        return $adbPath
    }
    Write-Verbose "adb.exe not found in PATH."

    # 2. Check common SDK locations (User Profile and System-wide)
    $commonSdkPaths = @(
        Join-Path $env:LOCALAPPDATA "Android\Sdk\platform-tools"
        Join-Path $env:ProgramFiles "Android\Android Studio\jre\bin" # Sometimes found here too
        Join-Path $env:ProgramFiles "(x86)\Android\android-sdk\platform-tools"
        Join-Path "C:\Users\20106\AppData\Local\Android\Sdk\platform-tools" # Common manual install location
    )
    foreach ($sdkPath in $commonSdkPaths) {
        if (Test-Path (Join-Path $sdkPath "adb.exe")) {
            Write-Host "[INFO] Found adb.exe in common location: $sdkPath" -ForegroundColor Cyan
            return $sdkPath
        }
        Write-Verbose "adb.exe not found in $sdkPath."
    }

    # 3. Fallback (Less reliable - specific to the original script's user)
    # $fallbackPath = "C:\Users\20106\AppData\Local\Android\Sdk\platform-tools"
    # if (Test-Path (Join-Path $fallbackPath "adb.exe")) {
    #     Write-Host "[WARN] Using hardcoded fallback ADB path: $fallbackPath. Consider adding ADB to your PATH." -ForegroundColor Yellow
    #     return $fallbackPath
    # }

    # Not Found
    Write-Host "[ERROR] ADB executable (adb.exe) could not be found!" -ForegroundColor Red
    Write-Host "        Please ensure the Android SDK Platform Tools are installed and" -ForegroundColor Red
    Write-Host "        that the 'platform-tools' directory is added to your system's PATH environment variable." -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    Exit 1
}

# --- Find ADB ---
$adbPath = Find-AdbPath
if (-not $adbPath) { Exit 1 } # Exit if Find-AdbPath failed
$adbFullName = Join-Path $adbPath "adb.exe"
$IsAdbValid = Test-Path $adbFullName
if (-not $IsAdbValid) {
    Write-Host "[ERROR] The determined ADB path seems invalid: '$adbFullName'" -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    Exit 1
}

#endregion

#region --- Helper Functions ---

# Improved function to execute ADB commands
function Invoke-AdbCommand {
    param(
        [Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)]
        [string[]]$Arguments,
        [switch]$HideStatusMessages, # Don't show [EXEC], [OK], [FAIL]
        [switch]$CaptureOutput       # Capture and return StdOut
    )

    $commandString = "adb $($Arguments -join ' ')"
    if (-not $HideStatusMessages) {
        Write-Host "`n[EXEC] $commandString" -ForegroundColor Cyan
    }

    try {
        # Execute and capture both stdout and stderr (2>&1)
        # Use $output variable to capture stdout stream
        $process = Start-Process -FilePath $adbFullName -ArgumentList $Arguments -NoNewWindow -PassThru -RedirectStandardOutput "$env:TEMP\adb_stdout.tmp" -RedirectStandardError "$env:TEMP\adb_stderr.tmp" -Wait

        $stdout = Get-Content "$env:TEMP\adb_stdout.tmp" -Raw -ErrorAction SilentlyContinue
        $stderr = Get-Content "$env:TEMP\adb_stderr.tmp" -Raw -ErrorAction SilentlyContinue
        Remove-Item "$env:TEMP\adb_stdout.tmp", "$env:TEMP\adb_stderr.tmp" -ErrorAction SilentlyContinue

        $exitCode = $process.ExitCode

        if ($exitCode -eq 0) {
            if (-not $HideStatusMessages) {
                Write-Host "[ OK ] Command executed successfully." -ForegroundColor Green
            }
            if ($CaptureOutput) {
                return $stdout # Return captured output
            } else {
                 # Print output if not capturing, unless it's just whitespace
                if ($stdout -match '\S') { # Check if there is non-whitespace content
                    Write-Host "--- Output ---" -ForegroundColor DarkGray
                    Write-Host $stdout.Trim() -ForegroundColor White
                    Write-Host "--------------" -ForegroundColor DarkGray
                 }
            }
            # Display stderr even on success, as some tools output info there
             if ($stderr -match '\S') {
                 Write-Host "[WARN] Stderr Output:" -ForegroundColor Yellow
                 Write-Host $stderr.Trim() -ForegroundColor Yellow
             }

        } else {
            if (-not $HideStatusMessages) {
                Write-Host "[FAIL] Command exited with code: $exitCode." -ForegroundColor Red
            }
            # Always show stderr on failure
            if ($stderr -match '\S') {
                Write-Host "[ERROR] Details from Stderr:" -ForegroundColor Red
                Write-Host $stderr.Trim() -ForegroundColor Red
            } elseif ($stdout -match '\S') {
                # Show stdout if stderr is empty but stdout has info
                Write-Host "[INFO] Details from Stdout:" -ForegroundColor Yellow
                Write-Host $stdout.Trim() -ForegroundColor Yellow
            }

            if ($CaptureOutput) {
                # Return null or throw exception on failure when capturing? Let's return null.
                 return $null
            }
        }
    } catch {
        Write-Host "[FATAL] Failed to execute ADB command:" -ForegroundColor Red
        Write-Error $_
        if ($CaptureOutput) { return $null }
    } finally {
         # Add a blank line for spacing unless status messages were hidden
         if (-not $HideStatusMessages) { Write-Host }
    }
}

# Function to format and display help
function Show-Help {
    Write-Host "`n" + ("-" * 60) -ForegroundColor Cyan
    Write-Host (" " * 18 + "ADB Helper Shell Commands (v1.1)") -ForegroundColor Yellow
    Write-Host ("-" * 60) -ForegroundColor Cyan

    # Define commands with categories
    $commandGroups = @{
        "Connection & Server" = @(
            @{ Cmd = "ld"; Desc = "List connected devices and emulators (-l)" }
            @{ Cmd = "c";  Desc = "Connect to device via IP (use IP:Port field)" }
            @{ Cmd = "d";  Desc = "Disconnect device (use IP:Port field, or blank for all)" }
            @{ Cmd = "t";  Desc = "Restart ADB in TCP/IP mode on device (use Port field)" }
            @{ Cmd = "ss"; Desc = "Start the ADB server on PC" }
            @{ Cmd = "ks"; Desc = "Kill the ADB server on PC" }
            @{ Cmd = "v";  Desc = "Show ADB's Version" }
            @{ Cmd = "root"; Desc = "Restart ADB daemon with root permissions" }
            @{ Cmd = "rem"; Desc = "Remount System Partition as R/W (requires root)" }
        )
        "Device Interaction" = @(
            @{ Cmd = "s";  Desc = "Start ADB shell in a new console window" }
            @{ Cmd = "sc"; Desc = "Take screenshot and save to PC" }
            @{ Cmd = "r";  Desc = "Reboot Device (Normal)" }
            @{ Cmd = "rb"; Desc = "Reboot into Bootloader" }
            @{ Cmd = "rr"; Desc = "Reboot into Recovery" }
            @{ Cmd = "rfb";Desc = "Reboot into Fastbootd (Userspace Fastboot)" }
            @{ Cmd = "wake"; Desc = "Simulate Power Button press (toggle screen on/off)" }
        )
        "File Management" = @(
            @{ Cmd = "push"; Desc = "Push File (PC -> Device) - Select PC file, enter Device path" }
            @{ Cmd = "pull"; Desc = "Pull File (Device -> PC) - Enter Device file path, select PC folder" }
        )
        "Application Management" = @(
            @{ Cmd = "lp";   Desc = "List Installed Packages" }
            @{ Cmd = "lpf";  Desc = "List Packages with File Locations" }
            @{ Cmd = "lp3";  Desc = "List only Third-Party Packages" }
            @{ Cmd = "i";    Desc = "Install APK - Select APK file (-r flag included)" }
            @{ Cmd = "u";    Desc = "Uninstall APK (Requires Package Name)" }
            @{ Cmd = "dis";  Desc = "Disable App for current user (pm disable-user) (Requires Pkg Name)" }
            @{ Cmd = "en";   Desc = "Enable a previously disabled App (pm enable) (Requires Pkg Name)" }
            @{ Cmd = "clr";  Desc = "Clear App Data (Confirmation required) (Requires Pkg Name)" }
            @{ Cmd = "fs";   Desc = "Force Stop App (am force-stop) (Requires Pkg Name)" }
        )
        "Device Properties" = @(
            @{ Cmd = "gbri"; Desc = "Get current screen brightness (0-255)" }
            @{ Cmd = "sbri"; Desc = "Set screen brightness (use Brightness field) [!] May need permission" }
            @{ Cmd = "gser"; Desc = "Get Device Serial Number" }
            @{ Cmd = "gmod"; Desc = "Get Device Model Name" }
            @{ Cmd = "gos";  Desc = "Get Android Version (e.g., 11, 12)" }
            @{ Cmd = "gbld"; Desc = "Get detailed Build Number/ID" }
            @{ Cmd = "gbat"; Desc = "Get Battery Status (raw dumpsys battery output)" }
            @{ Cmd = "gres"; Desc = "Get Screen Resolution (raw wm size output)" }
            @{ Cmd = "gip";  Desc = "Attempt to get device's main IP address" }
            @{ Cmd = "lfeat";Desc = "List device hardware/software features" }
            @{ Cmd = "gmfr"; Desc = "Get Device Manufacturer Name" }
        )
        "Debugging & Logging" = @(
            @{ Cmd = "log";  Desc = "Start Logcat (streamed below, -v brief, Ctrl+C to stop)" }
            # Stop Logcat isn't really a command, it's just stopping the process.
        )
        "Script Controls" = @(
            @{ Cmd = "clear";Desc = "Clear this output screen" }
            @{ Cmd = "help"; Desc = "Show this help menu" }
            @{ Cmd = "exit"; Desc = "Exit the script" }
        )
    }

    # Define column widths
    $cmdWidth = 8
    $descWidth = 70 # Adjust as needed

    # Iterate through categories and commands
    $commandGroups.GetEnumerator() | ForEach-Object {
        Write-Host "`n>> $($_.Name)" -ForegroundColor Magenta
        Write-Host ("-" * ($_.Name.Length + 3)) -ForegroundColor DarkMagenta
        foreach ($item in $_.Value) {
            $cmdText = $item.Cmd.PadRight($cmdWidth)
            Write-Host "  " -NoNewline
            Write-Host $cmdText -ForegroundColor Green -NoNewline
            Write-Host $item.Desc -ForegroundColor White
        }
    }

    Write-Host ("-" * 60) -ForegroundColor Cyan
    Write-Host "[!] Commands requiring a Package Name will prompt for it if not provided as an argument." -ForegroundColor Yellow
    Write-Host "[!] Example: 'u com.example.app' or just 'u' then enter package name when prompted." -ForegroundColor Yellow
    Write-Host "`n"
}

# Helper to prompt for input if not provided
function Get-RequiredInput {
    param(
        [string]$PromptMessage,
        [string[]]$CurrentArgs,
        [int]$ArgIndex = 1 # Which argument index to check (0 is the command itself)
    )
    if ($CurrentArgs.Length -gt $ArgIndex) {
        return $CurrentArgs[$ArgIndex]
    } else {
        Write-Host "$PromptMessage`: " -ForegroundColor Yellow -NoNewline
        return Read-Host
    }
}

# Helper to prompt specifically for package name
function Get-PackageName {
    param(
        [string[]]$CurrentArgs
    )
    $pkg = Get-RequiredInput -PromptMessage "Enter Package Name (e.g., com.example.app)" -CurrentArgs $CurrentArgs -ArgIndex 1
    if (-not $pkg) {
        Write-Host "[WARN] Package name is required." -ForegroundColor Yellow
        return $null
    }
    return $pkg
}

# Helper for File/Folder Selection (Optional - Requires GUI interaction)
# You might prefer manual path entry in a pure shell script.
# Add -STA to powershell.exe if using these WPF dialogs.
# function Select-FileDialog {
#     param([string]$Title = "Select File", [string]$Filter = "All Files (*.*)|*.*")
#     Add-Type -AssemblyName System.Windows.Forms
#     $dialog = New-Object System.Windows.Forms.OpenFileDialog
#     $dialog.Title = $Title
#     $dialog.Filter = $Filter
#     if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
#         return $dialog.FileName
#     }
#     return $null
# }

# function Select-FolderDialog {
#     param([string]$Title = "Select Folder")
#      Add-Type -AssemblyName System.Windows.Forms
#      $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
#      $dialog.Description = $Title
#      if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
#          return $dialog.SelectedPath
#      }
#      return $null
# }

#endregion

#region --- Main Script Logic ---

Clear-Host
Write-Host ("=" * 60) -ForegroundColor Magenta
Write-Host (" " * 20 + "PowerShell ADB Helper") -ForegroundColor Magenta
Write-Host ("=" * 60) -ForegroundColor Magenta
Write-Host "ADB Path: $adbPath" -ForegroundColor DarkGray
Write-Host "Type 'help' for commands, 'exit' to quit."

# Main loop
do {
    # Get user input (command and potential arguments)
    Write-Host "`nPS ADB:\>" -ForegroundColor Yellow -NoNewline
    $userInput = Read-Host
    $tokens = $userInput.Trim() -split '\s+', 2 # Split into command and the rest of the arguments

    # Handle empty input
    if (-not $tokens[0]) { continue }

    $command = $tokens[0].ToLower() # Command is case-insensitive
    $arguments = if ($tokens.Length -gt 1) { @($tokens[1]) } else { @() } # Arguments keep their case if needed

    # --- Process Commands using Switch ---
    switch ($command) {
        # Connection & Server
        "ld" { Invoke-AdbCommand "devices" "-l" } # List Devices
        "c" { # Connect
            $ipPort = Get-RequiredInput -PromptMessage "Enter Device IP:Port (e.g., 192.168.1.100:5555)" -CurrentArgs $arguments -ArgIndex 0
            if ($ipPort) { Invoke-AdbCommand "connect" $ipPort } else { Write-Host "[WARN] IP Address:Port is required." -ForegroundColor Yellow }
        }
        "d" { # Disconnect
            Write-Host "Enter IP:Port to disconnect (or leave blank for all): " -ForegroundColor Yellow -NoNewline
            $ipPort = Read-Host # Allow blank input easily
            if ($ipPort) { Invoke-AdbCommand "disconnect" $ipPort } else { Invoke-AdbCommand "disconnect" }
        }
        "t" { # TCP/IP Mode
            $port = Get-RequiredInput -PromptMessage "Enter Port for TCP/IP mode (e.g., 5555)" -CurrentArgs $arguments -ArgIndex 0
            if ($port -match '^\d+$') { Invoke-AdbCommand "tcpip" $port } else { Write-Host "[WARN] Invalid or missing port number." -ForegroundColor Yellow }
        }
        "ss" { Invoke-AdbCommand "start-server" } # Start Server
        "ks" { Invoke-AdbCommand "kill-server" } # Kill Server
        "v" { Invoke-AdbCommand "version" } # Version
        "root" { Invoke-AdbCommand "root" } # ADB Root
        "rem" { Invoke-AdbCommand "remount" } # Remount System

        # Device Interaction
        "s" { # Start Shell
            Write-Host "`nStarting ADB shell in new window... (Type 'exit' in the shell to close it)" -ForegroundColor Cyan
            # Start-Process powershell "-NoExit -Command & '$adbFullName' shell" # Keeps PS window open after exit
            Start-Process "$adbFullName" "shell" # More direct, closes when shell exits
        }
        "sc" { # Screenshot
            $defaultFileName = "screenshot_$(Get-Date -Format 'yyyyMMdd_HHmmss').png"
            Write-Host "Enter PC path to save screenshot (or press Enter for Desktop\$defaultFileName): " -ForegroundColor Yellow -NoNewline
            $pcPath = Read-Host
            if (-not $pcPath) {
                $desktopPath = [Environment]::GetFolderPath('Desktop')
                $pcPath = Join-Path $desktopPath $defaultFileName
            } elseif ((Test-Path $pcPath -PathType Container) -or $pcPath.EndsWith('\') -or $pcPath.EndsWith('/')) {
                 # If user provided a directory, append default filename
                 $pcPath = Join-Path $pcPath $defaultFileName
            }
            # Ensure directory exists
             $pcDir = Split-Path $pcPath -Parent
             if (-not (Test-Path $pcDir)) {
                 Write-Host "[INFO] Creating directory: $pcDir" -ForegroundColor Cyan
                 New-Item -ItemType Directory -Path $pcDir -Force | Out-Null
             }

            Write-Host "[INFO] Taking screenshot..." -ForegroundColor Cyan
            $deviceTempPath = "/sdcard/screenshot_temp.png" # Use a known temp location
            Invoke-AdbCommand "shell" "screencap" "-p" "$deviceTempPath" -HideStatusMessages # Capture
            Write-Host "[INFO] Downloading screenshot to '$pcPath'..." -ForegroundColor Cyan
            Invoke-AdbCommand "pull" "$deviceTempPath" "$pcPath" -HideStatusMessages # Pull
            Invoke-AdbCommand "shell" "rm" "$deviceTempPath" -HideStatusMessages # Clean up
            Write-Host "[ OK ] Screenshot saved to $pcPath" -ForegroundColor Green
        }
        "r"   { Invoke-AdbCommand "reboot" } # Reboot
        "rb"  { Invoke-AdbCommand "reboot" "bootloader" } # Reboot Bootloader
        "rr"  { Invoke-AdbCommand "reboot" "recovery" } # Reboot Recovery
        "rfb" { Invoke-AdbCommand "reboot" "fastboot" } # Reboot Fastbootd
        "wake"{ Invoke-AdbCommand "shell" "input" "keyevent" "KEYCODE_POWER" } # Wake/Sleep Toggle

        # File Management
        "push" { # Push File
            Write-Host "Enter FULL path of the file on your PC: " -ForegroundColor Yellow -NoNewline
            $localPath = Read-Host
            Write-Host "Enter destination path on the Android device (e.g., /sdcard/Download/): " -ForegroundColor Yellow -NoNewline
            $devicePath = Read-Host
            if ($localPath -and $devicePath -and (Test-Path $localPath -PathType Leaf)) {
                Invoke-AdbCommand "push" $localPath $devicePath
            } elseif (-not (Test-Path $localPath -PathType Leaf)) {
                Write-Host "[ERROR] Local file '$localPath' not found or is a directory." -ForegroundColor Red
            } else { Write-Host "[WARN] Both local and device paths are required." -ForegroundColor Yellow }
        }
        "pull" { # Pull File
            Write-Host "Enter FULL path of the file/folder on the Android device: " -ForegroundColor Yellow -NoNewline
            $devicePath = Read-Host
            Write-Host "Enter destination folder path on your PC (e.g., C:\Downloads\): " -ForegroundColor Yellow -NoNewline
            $localPath = Read-Host
            if ($localPath -and $devicePath) {
                # Ensure local directory exists
                if (-not (Test-Path $localPath -PathType Container)) {
                     Write-Host "[INFO] Creating directory: $localPath" -ForegroundColor Cyan
                     New-Item -ItemType Directory -Path $localPath -Force | Out-Null
                }
                Invoke-AdbCommand "pull" $devicePath $localPath
            } else { Write-Host "[WARN] Both device and local paths are required." -ForegroundColor Yellow }
        }

        # Application Management
        "lp"  { Invoke-AdbCommand "shell" "pm" "list" "packages" } # List Packages
        "lpf" { Invoke-AdbCommand "shell" "pm" "list" "packages" "-f" } # List Packages + Path
        "lp3" { Invoke-AdbCommand "shell" "pm" "list" "packages" "-3" } # List 3rd Party Packages
        "i" { # Install APK
            Write-Host "Enter FULL path of the APK file on your PC: " -ForegroundColor Yellow -NoNewline
            $apkPath = Read-Host
            if ($apkPath -and (Test-Path $apkPath -PathType Leaf) -and $apkPath.ToLower().EndsWith(".apk")) {
                Invoke-AdbCommand "install" "-r" $apkPath # Add -r to allow reinstall/downgrade
            } elseif ($apkPath -and -not $apkPath.ToLower().EndsWith(".apk")) {
                Write-Host "[ERROR] File does not appear to be an APK: '$apkPath'" -ForegroundColor Red
            } elseif ($apkPath -and -not (Test-Path $apkPath -PathType Leaf)) {
                Write-Host "[ERROR] Local file '$apkPath' not found or is a directory." -ForegroundColor Red
            } else { Write-Host "[WARN] APK file path is required." -ForegroundColor Yellow }
        }
        "u" { # Uninstall APK
            $packageName = Get-PackageName -CurrentArgs $arguments
            if ($packageName) { Invoke-AdbCommand "uninstall" $packageName }
        }
        "dis" { # Disable App
            $packageName = Get-PackageName -CurrentArgs $arguments
            if ($packageName) { Invoke-AdbCommand "shell" "pm" "disable-user" "--user" "0" $packageName }
        }
        "en" { # Enable App
            $packageName = Get-PackageName -CurrentArgs $arguments
            if ($packageName) { Invoke-AdbCommand "shell" "pm" "enable" $packageName }
        }
        "clr" { # Clear Data
            $packageName = Get-PackageName -CurrentArgs $arguments
            if ($packageName) {
                 Write-Host "ARE YOU SURE you want to clear all data for '$packageName'? (This cannot be undone!)" -ForegroundColor Red
                 Write-Host "Type 'YES' to confirm: " -ForegroundColor Yellow -NoNewline
                 $confirmation = Read-Host
                 if ($confirmation -eq 'YES') {
                     Invoke-AdbCommand "shell" "pm" "clear" $packageName
                 } else {
                     Write-Host "[CANCELLED] Clear data operation aborted." -ForegroundColor Yellow
                 }
            }
        }
        "fs" { # Force Stop
            $packageName = Get-PackageName -CurrentArgs $arguments
            if ($packageName) { Invoke-AdbCommand "shell" "am" "force-stop" $packageName }
        }

        # Device Properties
        "gbri" { # Get Brightness
             Write-Host "[INFO] Getting screen brightness..." -ForegroundColor Cyan
             Invoke-AdbCommand "shell" "settings" "get" "system" "screen_brightness"
        }
        "sbri" { # Set Brightness
            $brightness = Get-RequiredInput -PromptMessage "Enter Brightness value (0-255)" -CurrentArgs $arguments -ArgIndex 0
            if ($brightness -match '^\d+$' -and [int]$brightness -ge 0 -and [int]$brightness -le 255) {
                Write-Host "[WARN] Setting brightness requires WRITE_SETTINGS permission." -ForegroundColor Yellow
                Write-Host "        You might need to grant it first via:" -ForegroundColor Yellow
                Write-Host "        adb shell pm grant $ExecutionContext.SessionState.Application.PackageName android.permission.WRITE_SETTINGS" -ForegroundColor Yellow # Might need adjustment based on how script is run
                 Invoke-AdbCommand "shell" "settings" "put" "system" "screen_brightness" $brightness
            } else { Write-Host "[WARN] Invalid or missing brightness value (must be 0-255)." -ForegroundColor Yellow }
        }
        "gser" { Invoke-AdbCommand "get-serialno" } # Get Serial
        "gmod" { Invoke-AdbCommand "shell" "getprop" "ro.product.model" } # Get Model
        "gos"  { Invoke-AdbCommand "shell" "getprop" "ro.build.version.release" } # Get OS Version
        "gbld" { Invoke-AdbCommand "shell" "getprop" "ro.build.display.id" } # Get Build ID
        "gbat" { Invoke-AdbCommand "shell" "dumpsys" "battery" } # Get Battery
        "gres" { Invoke-AdbCommand "shell" "wm" "size" } # Get Resolution
        "gip"  { # Get IP Address (Attempt)
            Write-Host "[INFO] Attempting to find device IP (might show multiple interfaces)..." -ForegroundColor Cyan
            Invoke-AdbCommand "shell" "ip" "addr" "show" # More reliable than ifconfig on newer Android
        }
        "lfeat"{ Invoke-AdbCommand "shell" "pm" "list" "features" } # List Features
        "gmfr" { Invoke-AdbCommand "shell" "getprop" "ro.product.manufacturer" } # Get Manufacturer

        # Debugging & Logging
        "log" { # Start Logcat
            Write-Host "`nStarting Logcat (-v brief)... Press CTRL+C in this window to stop." -ForegroundColor Cyan
            # Direct execution to allow Ctrl+C to break it
            & $adbFullName logcat -v brief
            # Catch the Ctrl+C break gracefully if possible (or just let it terminate)
            trap [System.Management.Automation.PipelineStoppedException] {
                Write-Host "`nLogcat stream stopped." -ForegroundColor Cyan
                continue # Continue the main script loop
            }
            Write-Host "`nLogcat stream finished or was stopped." -ForegroundColor Cyan
        }
        # Stop Logcat is handled by Ctrl+C

        # Script Controls
        "clear" { Clear-Host }
        "cls"   { Clear-Host } # Alias for clear
        "help"  { Show-Help }
        "exit"  {
            Write-Host "`nExiting ADB Helper. Goodbye!" -ForegroundColor Green
            break # Exit the do..while loop
        }

        # Default case for unknown commands
        default {
            Write-Host "`n[ERROR] Unknown command: '$command'. Type 'help' for available commands." -ForegroundColor Red
        }
    } # End Switch

} while ($true) # End Main Loop

#endregion

# Final cleanup (if any needed)
Write-Host "Script finished."