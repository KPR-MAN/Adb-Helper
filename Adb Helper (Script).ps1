#region --- Configuration and ADB Path Detection ---

# Try finding ADB in PATH
$adbExecutable = Get-Command adb.exe -ErrorAction SilentlyContinue
if ($adbExecutable) {
    $adbPath = Split-Path $adbExecutable.Path -Parent
    Write-Host "[INFO] Found adb.exe in PATH: $adbPath" -ForegroundColor Cyan
} else {
    # Try default SDK location
    $defaultSdkPath = Join-Path $env:LOCALAPPDATA "Android\Sdk\platform-tools"
    if (Test-Path (Join-Path $defaultSdkPath "adb.exe")) {
        $adbPath = $defaultSdkPath
        Write-Host "[INFO] Found adb.exe in default SDK location: $adbPath" -ForegroundColor Cyan
    } else {
        # Fallback to hardcoded path (Update if necessary)
        $fallbackPath = "C:\Users\20106\AppData\Local\Android\Sdk\platform-tools"
        if (Test-Path (Join-Path $fallbackPath "adb.exe")) {
            $adbPath = $fallbackPath
            Write-Host "[INFO] Using fallback ADB path: $adbPath" -ForegroundColor Yellow
        } else {
            Write-Host "[ERROR] adb.exe not found in PATH, default SDK location, or fallback path ($fallbackPath)." -ForegroundColor Red
            Write-Host "[ERROR] Please ensure ADB is installed and its directory is in your PATH, or update the fallback path in the script." -ForegroundColor Red
            Read-Host "Press Enter to exit..."
            Exit 1
        }
    }
}

$adbFullName = Join-Path $adbPath "adb.exe"

#endregion

#region --- Helper Functions ---

# Function to execute ADB commands and provide feedback
function Invoke-AdbCommand {
    param(
        [Parameter(Mandatory=$true, Position=0, ValueFromRemainingArguments=$true)]
        [string[]]$Arguments
    )

    Write-Host "`n[EXEC] adb $($Arguments -join ' ')" -ForegroundColor Cyan
    try {
        # Use Start-Process to better capture output/errors if needed later,
        # but for now, direct invocation is fine and simpler.
        & $adbFullName $Arguments # *>&1 # Uncomment to merge error stream with output

        if ($LASTEXITCODE -eq 0) {
             Write-Host "[ OK ] Command executed successfully." -ForegroundColor Green
        } else {
             Write-Host "[FAIL] Command exited with code: $LASTEXITCODE." -ForegroundColor Red
             # Consider adding more specific error handling based on common exit codes if needed
        }
    } catch {
        Write-Host "[ERROR] Failed to execute ADB command:" -ForegroundColor Red
        Write-Error $_
    }
    Write-Host # Add a blank line for spacing
}

# Function to show the help menu with colors
function Show-Help {
    Write-Host "`n" # Blank line before help
    Write-Host "_______________________________________" -ForegroundColor Cyan
    Write-Host "         ADB Helper Commands         " -ForegroundColor Yellow
    Write-Host "---------------------------------------" -ForegroundColor Cyan

    # Define the commands and descriptions in a hashtable
    $commands = @{
        "-c"    = "Connect to device via IP"
        "-d"    = "Disconnect device via IP"
        "-t"    = "Restart ADB in TCP/IP mode on device"
        "-ss"   = "Start the ADB server"
        "-ks"   = "Kill the ADB server"
        "-av"   = "Show ADB's Version"
        "-s"    = "Start ADB shell"
        "-pft"  = "Push File (PC -> Device)"
        "-ptf"  = "Pull File (Device -> PC)"
        "-i"    = "Install APK"
        "-u"    = "Uninstall APK (by package name)"
        "-r"    = "Reboot Device (Normal)"
        "-rb"   = "Reboot into Bootloader"
        "-rr"   = "Reboot into Recovery"
        "-root" = "Restart ADB daemon with root permissions"
        "-re-m" = "Remount System Partition (requires root)"
        "-lp"   = "List Installed Packages"
        "-lpl"  = "List Packages with File Locations"
        "-da"   = "Disable App (by package name)"
        "-e"    = "Enable App (by package name)"
        "-lc"   = "Output device Logcat"
        "help"  = "Shows this help menu"
        "clear" = "Clear the screen"
        "exit"  = "Exits the Script"
    }

    # Format the hashtable into a table with custom headers
    # Use calculated properties to define column names and content
    $commands.GetEnumerator() | Sort-Object Name | Format-Table -Property @(
        @{Label="Command"; Expression={$_.Name}; Alignment="Left"}
        @{Label="Description"; Expression={$_.Value}; Alignment="Left"}
    ) -AutoSize | Out-String | ForEach-Object {
        # Colorize the output from Format-Table
        $line = $_.TrimEnd() # Remove trailing spaces for cleaner matching
        if ($line -match '^\s*(-[\w-]+)\s+(.*)') { # Match commands starting with '-'
            $command = $matches[1]
            $description = $matches[2]
            Write-Host (" " * ($line.IndexOf($command))) -NoNewline # Preserve leading space for alignment
            Write-Host $command -ForegroundColor Green -NoNewline
            Write-Host (" " * ($line.IndexOf($description) - ($line.IndexOf($command) + $command.Length))) -NoNewline # Spaces between
            Write-Host $description -ForegroundColor White
        } elseif ($line -match '^\s*(help|clear|exit)\s+(.*)') { # Match other specific commands
             $command = $matches[1]
             $description = $matches[2]
             Write-Host (" " * ($line.IndexOf($command))) -NoNewline # Preserve leading space
             Write-Host $command -ForegroundColor Green -NoNewline
             Write-Host (" " * ($line.IndexOf($description) - ($line.IndexOf($command) + $command.Length))) -NoNewline # Spaces between
             Write-Host $description -ForegroundColor White
        } elseif ($line -match '^Command\s+Description') { # Match the header line
             Write-Host $line -ForegroundColor Gray
        } elseif ($line -match '^-{4,}\s+-{5,}$') { # Match the separator line '---- -----------'
             Write-Host $line -ForegroundColor DarkGray
        } elseif ($line.Trim() -ne "") { # Catch any other non-empty lines (shouldn't happen often)
            Write-Host $line -ForegroundColor Gray
        }
        # Don't print blank lines generated by Out-String unless intended
    }

    Write-Host "_______________________________________" -ForegroundColor Cyan
    Write-Host "`n" # Blank line after help
}

#endregion

#region --- Main Script Logic ---

Clear-Host
Write-Host "=========================" -ForegroundColor Magenta
Write-Host "        ADB Helper       " -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta
Write-Host "ADB Path: $adbPath" -ForegroundColor DarkGray
Write-Host "Type 'help' for commands, 'exit' to quit."

# Main loop for user input
do {
    # Use -NoNewline to keep input on the same line as the prompt
    Write-Host "`nRun -> " -ForegroundColor Yellow -NoNewline
    $operation = Read-Host

    switch ($operation.ToLower()) { # Convert to lowercase for case-insensitivity
        "help" {
            Show-Help
        }
        "-c" {
            Write-Host "Enter IP Address (e.g., 192.168.1.100:5555): " -ForegroundColor Yellow -NoNewline
            $inputIp = Read-Host
            if ($inputIp) { Invoke-AdbCommand "connect" $inputIp } else { Write-Host "[WARN] No IP Address entered." -ForegroundColor Yellow }
        }
        "-d" {
            Write-Host "Enter IP Address to disconnect (or leave blank for all): " -ForegroundColor Yellow -NoNewline
            $inputIp = Read-Host
            if ($inputIp) { Invoke-AdbCommand "disconnect" $inputIp } else { Invoke-AdbCommand "disconnect" }
        }
        "-t" {
            Write-Host "Enter TCP/IP Port (e.g., 5555): " -ForegroundColor Yellow -NoNewline
            $inputPort = Read-Host
            if ($inputPort -match '^\d+$') { Invoke-AdbCommand "tcpip" $inputPort } else { Write-Host "[WARN] Invalid port number entered." -ForegroundColor Yellow }
        }
        "-ss" {
            Invoke-AdbCommand "start-server"
        }
        "-ks" {
            Invoke-AdbCommand "kill-server"
        }
        "-av" {
            Invoke-AdbCommand "version"
        }
        "-s" {
            # Shell is interactive, so Invoke-AdbCommand might not be ideal if we expect script control back immediately.
            # Direct call is better here.
            Write-Host "`nStarting ADB shell... (Type 'exit' in the shell to return here)" -ForegroundColor Cyan
            & $adbFullName shell
            Write-Host "Exited ADB shell." -ForegroundColor Cyan
        }
        "-pft" {
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
        "-ptf" {
            Write-Host "Enter FULL path of the file on the Android device: " -ForegroundColor Yellow -NoNewline
            $devicePath = Read-Host
            Write-Host "Enter destination path on your PC (e.g., C:\Downloads\): " -ForegroundColor Yellow -NoNewline
            $localPath = Read-Host
            if ($localPath -and $devicePath) { Invoke-AdbCommand "pull" $devicePath $localPath } else { Write-Host "[WARN] Both device and local paths are required." -ForegroundColor Yellow }
        }
        "-i" {
            Write-Host "Enter FULL path of the APK file on your PC: " -ForegroundColor Yellow -NoNewline
            $apkPath = Read-Host
            if ($apkPath -and (Test-Path $apkPath -PathType Leaf) -and $apkPath.EndsWith(".apk")) {
                Invoke-AdbCommand "install" $apkPath
            } elseif (-not $apkPath.EndsWith(".apk")) {
                Write-Host "[ERROR] File does not appear to be an APK." -ForegroundColor Red
            } elseif (-not (Test-Path $apkPath -PathType Leaf)) {
                 Write-Host "[ERROR] Local file '$apkPath' not found or is a directory." -ForegroundColor Red
            } else { Write-Host "[WARN] APK file path is required." -ForegroundColor Yellow }
        }
        "-u" {
            Write-Host "Enter package name to uninstall (e.g., com.example.app): " -ForegroundColor Yellow -NoNewline
            $packageName = Read-Host
            if ($packageName) { Invoke-AdbCommand "uninstall" $packageName } else { Write-Host "[WARN] Package name is required." -ForegroundColor Yellow }
        }
        "-r" {
            Invoke-AdbCommand "reboot"
        }
        "-rb" {
            Invoke-AdbCommand "reboot" "bootloader"
        }
        "-rr" {
            Invoke-AdbCommand "reboot" "recovery"
        }
        "-root" {
            Invoke-AdbCommand "root"
        }
        "-re-m" {
            Invoke-AdbCommand "remount"
        }
        "-lp" {
            Invoke-AdbCommand "shell" "pm" "list" "packages"
        }
        "-lpl" {
            Invoke-AdbCommand "shell" "pm" "list" "packages" "-f"
        }
        "-da" {
            Write-Host "Enter package name to disable: " -ForegroundColor Yellow -NoNewline
            $packageName = Read-Host
            if ($packageName) { Invoke-AdbCommand "shell" "pm" "disable-user" "--user" "0" $packageName } else { Write-Host "[WARN] Package name is required." -ForegroundColor Yellow }
            # Note: Added --user 0 which is often needed for disable-user
        }
        "-e" {
            Write-Host "Enter package name to enable: " -ForegroundColor Yellow -NoNewline
            $packageName = Read-Host
            if ($packageName) { Invoke-AdbCommand "shell" "pm" "enable" $packageName } else { Write-Host "[WARN] Package name is required." -ForegroundColor Yellow }
        }
        "-lc" {
            # Logcat can run indefinitely, similar to shell. Direct call is better.
             Write-Host "`nStarting Logcat... (Press CTRL+C to stop)" -ForegroundColor Cyan
             & $adbFullName logcat
             Write-Host "Logcat stopped." -ForegroundColor Cyan
        }
        "clear" {
            Clear-Host
            # Optional: Reprint header after clearing
            # Write-Host "=========================" -ForegroundColor Magenta
            # Write-Host " PowerShell ADB Helper " -ForegroundColor Magenta
            # Write-Host "=========================" -ForegroundColor Magenta
            # Write-Host "ADB Path: $adbPath" -ForegroundColor DarkGray
            # Write-Host "Type 'help' for commands, 'exit' to quit."
        }
        "exit" {
            Write-Host "`nGoodbye!" -ForegroundColor Green
            break # Exit the do..while loop
        }
        default {
            # Ignore empty input (pressing Enter without typing)
            if ($operation -ne '') {
                 Write-Host "`n[ERROR] Invalid option: '$operation'. Type 'help' for available commands." -ForegroundColor Red
            }
        }
    }
} while ($true)

#endregion