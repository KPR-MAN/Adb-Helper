import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, font
import subprocess
import os
import sys
import shutil
import threading
import time # Added for screenshot filename

# --- Configuration ---
WINDOW_TITLE = "ADB Helper GUI v1.1" # <<<--- SET TITLE AS REQUESTED
WINDOW_GEOMETRY = "850x750" # Increased size slightly for more buttons/fields
DEFAULT_BACKGROUND_COLOR = "#2E2E2E"
TEXT_AREA_BG = "#1E1E1E"
TEXT_AREA_FG = "#DCDCDC"
BUTTON_BG = "#4A4A4A"
BUTTON_FG = "#FFFFFF"
LABEL_FG = "#E0E0E0"
ENTRY_BG = "#3C3C3C"
ENTRY_FG = "#FFFFFF"
INFO_COLOR = "#40E0D0" # Cyan
OK_COLOR = "#32CD32"   # LimeGreen
WARN_COLOR = "#FFD700" # Gold
ERROR_COLOR = "#FF4500" # OrangeRed
EXEC_COLOR = "#6495ED" # CornflowerBlue

# --- Global Variables ---
adb_executable_path = None
logcat_process = None
is_stopping_logcat = False # Flag to prevent double-stopping messages

# --- ADB Path Detection ---
def find_adb_path():
    """Tries to find adb.exe in PATH, common locations."""
    global adb_executable_path
    adb_exe = "adb.exe" if sys.platform == "win32" else "adb" # Adapt for non-Windows

    # 1. Check PATH
    adb_path_in_env = shutil.which(adb_exe)
    if adb_path_in_env:
        adb_executable_path = adb_path_in_env
        log_message(f"[INFO] Found ADB in PATH: {adb_executable_path}", INFO_COLOR)
        return adb_executable_path

    # 2. Check common SDK locations (Windows)
    if sys.platform == "win32":
        common_paths = [
            os.path.join(os.getenv('LOCALAPPDATA', ''), "Android", "Sdk", "platform-tools", adb_exe),
            os.path.join(os.getenv('ProgramFiles', ''), "Android", "Sdk", "platform-tools", adb_exe),
            os.path.join(os.getenv('ProgramFiles(x86)', ''), "Android", "Sdk", "platform-tools", adb_exe),
            os.path.join(os.getenv('USERPROFILE', ''), "AppData", "Local", "Android", "Sdk", "platform-tools", adb_exe) # Fallback added here
        ]
        for path in common_paths:
            if path and os.path.exists(path):
                adb_executable_path = path
                log_message(f"[INFO] Found ADB in common location: {adb_executable_path}", INFO_COLOR)
                return adb_executable_path

    # 3. Add common paths for Linux/macOS
    elif sys.platform in ["linux", "darwin"]:
        home = os.path.expanduser("~")
        common_paths = [
            os.path.join(home, "Android/Sdk/platform-tools", adb_exe),
            os.path.join(home, "android-sdk/platform-tools", adb_exe),
            "/usr/lib/android-sdk/platform-tools/" + adb_exe, # Common Linux install path
            "/opt/android-sdk/platform-tools/" + adb_exe,
        ]
        for path in common_paths:
             if os.path.exists(path):
                 adb_executable_path = path
                 log_message(f"[INFO] Found ADB in common location: {adb_executable_path}", INFO_COLOR)
                 return adb_executable_path

    log_message("[ERROR] ADB executable not found automatically.", ERROR_COLOR)
    log_message("[ERROR] Please ensure ADB is installed and in your system's PATH.", ERROR_COLOR)
    log_message("[INFO] You can manually specify the path if needed (requires code modification).", INFO_COLOR)
    messagebox.showerror("ADB Not Found", "Could not locate the ADB executable. Please ensure it's installed and added to your system's PATH environment variable.")
    return None


# --- Helper Functions ---
def run_adb_command(args, display_output=True, command_name="Command", sync=False):
    """
    Executes an ADB command and logs output.
    Can run asynchronously (default) or synchronously.
    Returns Popen process object if async, or (stdout, stderr, returncode) if sync.
    """
    global logcat_process, is_stopping_logcat
    if not adb_executable_path:
        log_message("[ERROR] ADB path not set. Cannot run command.", ERROR_COLOR)
        return None if not sync else ("", "ADB path not set", -1)

    # Handle shell commands with pipes/redirects carefully for sync execution
    is_shell_complex = False
    if "shell" in args and ("|" in args or ">" in args or "<" in args):
        is_shell_complex = True
        # On Windows, complex shell commands need 'cmd /c "adb shell ..."'
        # On Linux/macOS, 'sh -c "adb shell ..."' might be needed or direct execution might work
        if sys.platform == "win32":
             full_command_str = subprocess.list2cmdline([adb_executable_path] + args)
             # Rebuild command list for Popen/run with shell=True
             command = f'cmd /c "{full_command_str}"' # Pass as string for shell=True
             use_shell_true = True
        else:
             # For Linux/macOS, Popen/run often handles pipes better without explicit shell wrapper
             # Keep original command list for now, rely on subprocess internals
             command = [adb_executable_path] + args
             use_shell_true = False # Generally safer not to use shell=True unless needed
             # If issues arise, might need: command = f'sh -c "{subprocess.list2cmdline(command)}"' and use_shell_true = True
    else:
        command = [adb_executable_path] + args
        use_shell_true = False


    log_message(f"\n[EXEC] {' '.join(args)}", EXEC_COLOR) # Log the ADB part, not the wrapper

    def command_thread_target():
        global logcat_process, is_stopping_logcat
        try:
            process = subprocess.Popen(
                command, # Use modified command if needed
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                shell=use_shell_true # Set shell=True if using wrapper like cmd /c
            )

            # Special handling for streaming logcat
            is_logcat_streaming = isinstance(args, list) and args and args[0] == 'logcat' and args[-1] != '-d'
            if is_logcat_streaming:
                logcat_process = process
                is_stopping_logcat = False # Reset flag when starting
                log_message(f"[ OK ] {command_name} started. Streaming... (Use 'Stop Logcat')", OK_COLOR)
                for line in iter(process.stdout.readline, ''):
                    if is_stopping_logcat or logcat_process != process: # Check flag or if process changed
                        log_message("[INFO] Logcat stream stopping...", INFO_COLOR)
                        break
                    log_message(line.strip(), TEXT_AREA_FG)

                process.stdout.close()
                # Ensure termination if stop was requested
                if (is_stopping_logcat or logcat_process != process) and process.poll() is None:
                    try:
                        process.terminate()
                    except Exception: pass # Ignore errors during termination

                return_code = process.wait()
                stderr_output = process.stderr.read()
                process.stderr.close()

                logcat_process = None # Clear the global process tracker
                is_stopping_logcat = False # Reset flag
                log_message(f"[INFO] Logcat stream stopped (Code: {return_code}).", INFO_COLOR)

                if stderr_output:
                    log_message(f"[STDERR]\n{stderr_output.strip()}", WARN_COLOR)

            else: # For non-streaming commands
                stdout_output, stderr_output = process.communicate()
                return_code = process.returncode

                if display_output and stdout_output:
                    log_message(f"[STDOUT]\n{stdout_output.strip()}")
                if stderr_output:
                    log_message(f"[STDERR]\n{stderr_output.strip()}", WARN_COLOR)

                if return_code == 0:
                    log_message(f"[ OK ] {command_name} executed successfully.", OK_COLOR)
                else:
                    log_message(f"[FAIL] {command_name} exited with code: {return_code}.", ERROR_COLOR)

        except FileNotFoundError:
            # Check if it was the shell (cmd, sh) or adb itself
            cmd_str = command if isinstance(command, str) else command[0]
            if use_shell_true and ("cmd" in cmd_str or "sh" in cmd_str):
                 log_message(f"[ERROR] Shell executable not found ({cmd_str}). Check system integrity.", ERROR_COLOR)
            else:
                 log_message(f"[ERROR] ADB executable not found at: {adb_executable_path}", ERROR_COLOR)
        except Exception as e:
            log_message(f"[ERROR] Failed to execute ADB command: {e}", ERROR_COLOR)
        finally:
            if 'process' in locals() and is_logcat_streaming and logcat_process == process:
                 logcat_process = None # Ensure it's cleared if thread ends unexpectedly
                 is_stopping_logcat = False
            log_message("", tag_color=None) # Add a blank line

    # Decide whether to run synchronously or asynchronously
    if sync:
        try:
            # Use subprocess.run for synchronous execution
            process = subprocess.run(
                command, # Use potentially modified command
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                check=False, # Don't raise exception on non-zero exit code
                shell=use_shell_true # Set shell=True if needed
            )
            stdout = process.stdout.strip() if process.stdout else ""
            stderr = process.stderr.strip() if process.stderr else ""
            retcode = process.returncode

            # Log output even for sync commands
            if stdout and display_output: log_message(f"[STDOUT]\n{stdout}")
            if stderr: log_message(f"[STDERR]\n{stderr}", WARN_COLOR)

            if retcode == 0:
                 log_message(f"[ OK ] {command_name} executed successfully (sync).", OK_COLOR)
            else:
                 log_message(f"[FAIL] {command_name} exited with code: {retcode} (sync).", ERROR_COLOR)
            log_message("", tag_color=None)
            return stdout, stderr, retcode

        except FileNotFoundError:
            cmd_str = command if isinstance(command, str) else command[0]
            if use_shell_true and ("cmd" in cmd_str or "sh" in cmd_str):
                 err_msg = f"Shell executable not found ({cmd_str})."
            else:
                 err_msg = f"ADB not found at {adb_executable_path}"
            log_message(f"[ERROR] {err_msg}", ERROR_COLOR)
            return "", err_msg, -1
        except Exception as e:
            log_message(f"[ERROR] Failed to execute sync ADB command: {e}", ERROR_COLOR)
            return "", str(e), -1
    else:
        # Start the command execution in a separate thread for async
        thread = threading.Thread(target=command_thread_target, daemon=True)
        thread.start()
        return None # Indicate async start


def log_message(message, tag_color=None):
    """Appends a message to the text area, applying color if specified."""
    try:
        if not root.winfo_exists(): return # Prevent errors during shutdown

        def _do_update():
            try:
                output_text.config(state=tk.NORMAL)
                if tag_color:
                    # Ensure tag exists
                    tag_name = f"color_{tag_color.replace('#', '')}"
                    if tag_name not in output_text.tag_names():
                         output_text.tag_config(tag_name, foreground=tag_color)
                    # Insert message with tag
                    output_text.insert(tk.END, message + "\n", tag_name)
                else:
                    # Insert message without specific tag (will use default fg)
                    output_text.insert(tk.END, message + "\n")
                output_text.see(tk.END) # Scroll to the end
                output_text.config(state=tk.DISABLED)
            except tk.TclError:
                 pass # Ignore errors if widget is destroyed
            except Exception as e:
                print(f"Error logging message: {e}") # Print to console if GUI fails

        # Schedule the update in the main Tkinter thread
        root.after(0, _do_update)

    except Exception as e:
        print(f"Error scheduling log message: {e}")


# --- Specific Command Functions ---

def list_devices():
    run_adb_command(["devices", "-l"], command_name="List Devices")

def connect_device():
    ip = ip_entry.get()
    if ip:
        run_adb_command(["connect", ip], command_name="Connect")
    else:
        log_message("[WARN] Please enter an IP Address (e.g., 192.168.1.100:5555).", WARN_COLOR)

def disconnect_device():
    ip = ip_entry.get()
    if ip:
        run_adb_command(["disconnect", ip], command_name="Disconnect Specific")
    else:
        run_adb_command(["disconnect"], command_name="Disconnect All") # Disconnect all

def set_tcpip_mode():
    port = port_entry.get()
    if port.isdigit():
        run_adb_command(["tcpip", port], command_name="Set TCP/IP Mode")
    else:
        log_message("[WARN] Please enter a valid port number (e.g., 5555).", WARN_COLOR)

def start_server():
    run_adb_command(["start-server"], command_name="Start Server")

def kill_server():
    run_adb_command(["kill-server"], command_name="Kill Server")

def show_version():
    run_adb_command(["version"], command_name="Show Version")

def start_shell():
    log_message("\n[INFO] Starting ADB shell in a new console window...", INFO_COLOR)
    log_message("[INFO] Type 'exit' in the new window to close it.", INFO_COLOR)
    if not adb_executable_path:
        log_message("[ERROR] ADB path not set.", ERROR_COLOR)
        return
    try:
        cmd_list = [adb_executable_path, "shell"]
        if sys.platform == "win32":
            # Use 'start' to detach the process and keep the GUI responsive
            # The extra '""' is often needed for 'start' if path contains spaces
            subprocess.Popen(['start', '""', '/WAIT', 'cmd', '/k'] + cmd_list, shell=True)
        elif sys.platform == "darwin":
            # Try opening with Terminal.app using osascript for better control
            script = f'tell application "Terminal" to do script "{subprocess.list2cmdline(cmd_list)}"'
            subprocess.Popen(['osascript', '-e', script])
        else: # Linux
             # Attempt common terminals
             terminals = ['x-terminal-emulator', 'gnome-terminal', 'konsole', 'xfce4-terminal', 'lxterminal', 'mate-terminal', 'terminator']
             opened = False
             # Prepare command string for terminals that use -e 'command args'
             cmd_str_for_e = subprocess.list2cmdline(cmd_list)
             for term in terminals:
                 try:
                     # Try different execution syntaxes common for terminals
                     if term in ['gnome-terminal', 'mate-terminal']: # Often use --
                         subprocess.Popen([term, '--', ' '.join(f'"{arg}"' for arg in cmd_list)])
                     else: # Assume -e for others
                         subprocess.Popen([term, '-e', cmd_str_for_e])
                     opened = True
                     log_message(f"[INFO] Opened shell using {term}.", INFO_COLOR)
                     break
                 except FileNotFoundError:
                     continue
                 except Exception as e_term:
                      log_message(f"[WARN] Failed attempt with {term}: {e_term}", WARN_COLOR)
                      continue # Try next terminal

             if not opened:
                 log_message("[ERROR] Could not find a known terminal emulator automatically.", ERROR_COLOR)
                 log_message("[INFO] Trying direct execution (output may be limited here).", INFO_COLOR)
                 run_adb_command(["shell"], command_name="Start Shell (Direct)", display_output=True) # Fallback

    except Exception as e:
        log_message(f"[ERROR] Could not open shell in new window: {e}", ERROR_COLOR)
        log_message("[INFO] Trying direct execution fallback.", INFO_COLOR)
        run_adb_command(["shell"], command_name="Start Shell (Direct)", display_output=True) # Fallback


def push_file():
    local_path = filedialog.askopenfilename(title="Select File to Push (PC)")
    if not local_path: return
    device_path = device_path_entry_push.get()
    if not device_path:
        device_path = "/sdcard/Download/" # Default if empty
        log_message(f"[INFO] No device path specified, using default: {device_path}", INFO_COLOR)
        # Update the entry field with the default path used
        device_path_entry_push.delete(0, tk.END)
        device_path_entry_push.insert(0, device_path)

    run_adb_command(["push", local_path, device_path], command_name="Push File")

def pull_file():
    device_path = device_path_entry_pull.get()
    if not device_path:
        log_message("[WARN] Please enter the full path of the file on the device.", WARN_COLOR)
        return
    local_path = filedialog.askdirectory(title="Select Destination Folder (PC)")
    if not local_path: return

    run_adb_command(["pull", device_path, local_path], command_name="Pull File")

def install_apk():
    apk_path = filedialog.askopenfilename(title="Select APK File to Install", filetypes=[("APK files", "*.apk")])
    if not apk_path: return
    run_adb_command(["install", "-r", apk_path], command_name="Install APK") # Added -r to allow reinstall/update

def uninstall_apk():
    package_name = package_name_entry.get()
    if package_name:
        run_adb_command(["uninstall", package_name], command_name="Uninstall APK")
    else:
        log_message("[WARN] Please enter the package name to uninstall.", WARN_COLOR)

def reboot_device(mode=""):
    command = ["reboot"]
    cmd_name = "Reboot Device"
    if mode == "bootloader":
        command.append("bootloader")
        cmd_name = "Reboot to Bootloader"
    elif mode == "recovery":
        command.append("recovery")
        cmd_name = "Reboot to Recovery"
    elif mode == "fastboot": # Added Fastbootd/Userspace Fastboot
        command.append("fastboot")
        cmd_name = "Reboot to Fastbootd"
    run_adb_command(command, command_name=cmd_name)

def root_adb():
    run_adb_command(["root"], command_name="Restart ADB as Root")

def remount_system():
    run_adb_command(["remount"], command_name="Remount System")

def list_packages(show_paths=False, only_third_party=False):
    command = ["shell", "pm", "list", "packages"]
    cmd_name = "List Packages"
    options = []
    if show_paths:
        options.append("-f")
        cmd_name += " with Paths"
    if only_third_party:
        options.append("-3")
        cmd_name += " (3rd Party)"

    command.extend(options)
    run_adb_command(command, command_name=cmd_name)

def clear_app_data():
    package_name = package_name_entry.get()
    if not package_name:
        log_message("[WARN] Please enter the package name to clear data.", WARN_COLOR)
        return
    # Add confirmation dialog
    if messagebox.askyesno("Confirm Clear Data", f"Are you sure you want to clear all data for '{package_name}'? This cannot be undone."):
        run_adb_command(["shell", "pm", "clear", package_name], command_name=f"Clear Data for {package_name}")
    else:
        log_message("[INFO] Clear data cancelled by user.", INFO_COLOR)

def force_stop_app():
    package_name = package_name_entry.get()
    if not package_name:
        log_message("[WARN] Please enter the package name to force stop.", WARN_COLOR)
        return
    run_adb_command(["shell", "am", "force-stop", package_name], command_name=f"Force Stop {package_name}")


def toggle_app(enable=True):
    package_name = package_name_entry.get()
    if not package_name:
        log_message("[WARN] Please enter the package name.", WARN_COLOR)
        return
    action = "enable" if enable else "disable-user"
    # Note: disable-user usually doesn't require --user 0, but enable might if disabled system app
    # Keep it simple unless issues arise.
    command = ["shell", "pm", action, package_name]
    # command = ["shell", "pm", action]
    # if not enable: # Add --user 0 only for disable-user? Might vary by Android version.
    #      command.extend(["--user", "0"])
    # command.append(package_name)
    cmd_name = f"{'Enable' if enable else 'Disable'} App {package_name}"
    run_adb_command(command, command_name=cmd_name)

def start_logcat():
    global logcat_process, is_stopping_logcat
    if logcat_process and logcat_process.poll() is None:
        log_message("[WARN] Logcat is already running.", WARN_COLOR)
        return
    logcat_process = None # Clear any stale process
    is_stopping_logcat = False
    # Run logcat without '-d' to keep it streaming
    run_adb_command(["logcat", "-v", "brief"], command_name="Start Logcat", display_output=False) # Added -v brief for slightly cleaner default output

def stop_logcat():
    global logcat_process, is_stopping_logcat
    if is_stopping_logcat: # Prevent triggering stop multiple times
        log_message("[INFO] Logcat stop already in progress...", INFO_COLOR)
        return

    if logcat_process and logcat_process.poll() is None: # Check if process exists and is running
        log_message("[INFO] Attempting to stop Logcat stream...", INFO_COLOR)
        is_stopping_logcat = True # Set flag immediately
        proc_to_stop = logcat_process
        logcat_process = None # Signal the reading thread loop to exit

        # Give the reading thread a moment to see the flag before terminating
        root.after(50, lambda: _terminate_logcat_process(proc_to_stop))

    else:
        log_message("[INFO] Logcat is not running or already stopped.", INFO_COLOR)
        logcat_process = None # Ensure it's cleared
        is_stopping_logcat = False # Reset flag if it wasn't running

def _terminate_logcat_process(process_to_terminate):
    """Helper to terminate the logcat process after a short delay."""
    global is_stopping_logcat
    try:
        if process_to_terminate.poll() is None: # Check again if it hasn't exited on its own
            process_to_terminate.terminate()
            try:
                # Wait briefly for terminate to work
                process_to_terminate.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                log_message("[WARN] Logcat did not terminate gracefully, killing...", WARN_COLOR)
                process_to_terminate.kill() # Force kill if terminate failed
                process_to_terminate.wait(timeout=1) # Wait briefly for kill
            except Exception as e_wait:
                 log_message(f"[WARN] Error during logcat wait/kill: {e_wait}", WARN_COLOR)

        # Final check after attempting termination
        if process_to_terminate.poll() is not None:
            log_message("[ OK ] Logcat process stopped.", OK_COLOR)
        else:
            log_message("[ERROR] Failed to stop the Logcat process.", ERROR_COLOR)

    except Exception as e:
        log_message(f"[ERROR] Exception while stopping Logcat process: {e}", ERROR_COLOR)
    finally:
        # Ensure flag is reset regardless of outcome
        is_stopping_logcat = False
        # Check if logcat_process was reassigned somehow, unlikely but safe
        if 'logcat_process' in globals() and logcat_process == process_to_terminate:
            logcat_process = None


def clear_output():
    try:
        output_text.config(state=tk.NORMAL)
        output_text.delete(1.0, tk.END)
        output_text.config(state=tk.DISABLED)
    except Exception as e:
        log_message(f"[ERROR] Failed to clear output: {e}", ERROR_COLOR)


# --- NEW Command Functions ---

def get_brightness():
    run_adb_command(["shell", "settings", "get", "system", "screen_brightness"], command_name="Get Brightness")

def set_brightness():
    brightness_value = brightness_entry.get()
    try:
        value = int(brightness_value)
        if 0 <= value <= 255:
            log_message(f"[INFO] Setting brightness to {value}. Note: This may require WRITE_SETTINGS permission on the device.", INFO_COLOR)
            run_adb_command(["shell", "settings", "put", "system", "screen_brightness", str(value)], command_name="Set Brightness")
        else:
            log_message("[WARN] Brightness value must be between 0 and 255.", WARN_COLOR)
    except ValueError:
        log_message("[WARN] Please enter a valid number (0-255) for brightness.", WARN_COLOR)

def get_device_model():
    run_adb_command(["shell", "getprop", "ro.product.model"], command_name="Get Device Model")

def get_android_version():
    run_adb_command(["shell", "getprop", "ro.build.version.release"], command_name="Get Android Version")

def get_build_number():
    run_adb_command(["shell", "getprop", "ro.build.display.id"], command_name="Get Build Number")

def get_battery_status():
    # Dumpsys output can be verbose, user needs to read relevant lines
    log_message("[INFO] Battery info follows (raw 'dumpsys battery' output):", INFO_COLOR)
    run_adb_command(["shell", "dumpsys", "battery"], command_name="Get Battery Status")

def get_screen_resolution():
    # wm size output needs parsing, e.g., "Physical size: 1080x1920"
    log_message("[INFO] Screen size info follows (raw 'wm size' output):", INFO_COLOR)
    run_adb_command(["shell", "wm", "size"], command_name="Get Screen Resolution")

def get_serial_number():
    run_adb_command(["get-serialno"], command_name="Get Serial Number")

def take_screenshot():
    """Takes a screenshot and saves it to the PC."""
    default_filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
    local_save_path = filedialog.asksaveasfilename(
        title="Save Screenshot As...",
        initialfile=default_filename,
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")]
    )
    if not local_save_path:
        log_message("[INFO] Screenshot cancelled.", INFO_COLOR)
        return

    # Use a dedicated thread for the sequence: screencap -> pull -> rm
    thread = threading.Thread(target=_thread_take_screenshot, args=(local_save_path,), daemon=True)
    thread.start()

def _thread_take_screenshot(local_save_path):
    """Worker thread for taking screenshot (runs commands synchronously)."""
    if not adb_executable_path:
        log_message("[ERROR] ADB path not set. Cannot take screenshot.", ERROR_COLOR)
        return

    device_temp_path = "/sdcard/adb_helper_screenshot.png"
    success = False

    try:
        # 1. Take screenshot on device (using synchronous run_adb_command)
        log_message(f"[INFO] Taking screenshot on device ({device_temp_path})...", INFO_COLOR)
        stdout_cap, stderr_cap, retcode_cap = run_adb_command(
            ["shell", "screencap", "-p", device_temp_path],
            command_name="Screenshot (Capture)",
            sync=True,
            display_output=False # Avoid double logging stdout/stderr
        )
        if retcode_cap != 0:
            log_message(f"[ERROR] Failed to capture screenshot on device. Code: {retcode_cap}", ERROR_COLOR)
            if stderr_cap: log_message(f"[STDERR] {stderr_cap}", WARN_COLOR)
            # Try to cleanup even if capture fails (file might exist from previous attempt)
        else:
             log_message("[ OK ] Screenshot captured on device.", OK_COLOR)


        # 2. Pull the screenshot from device (synchronous) - only if capture seemed ok
        if retcode_cap == 0:
            log_message(f"[INFO] Pulling screenshot to {local_save_path}...", INFO_COLOR)
            stdout_pull, stderr_pull, retcode_pull = run_adb_command(
                ["pull", device_temp_path, local_save_path],
                command_name="Screenshot (Pull)",
                sync=True,
                display_output=False
            )
            if retcode_pull != 0:
                log_message(f"[ERROR] Failed to pull screenshot from device. Code: {retcode_pull}", ERROR_COLOR)
                if stderr_pull: log_message(f"[STDERR] {stderr_pull}", WARN_COLOR)
                # Continue to delete temp file anyway
            else:
                success = True
                log_message("[ OK ] Screenshot pulled successfully.", OK_COLOR)

        # 3. Remove the temporary screenshot from device (synchronous)
        # Always attempt cleanup if the capture command was issued
        log_message(f"[INFO] Removing temporary file ({device_temp_path}) from device...", INFO_COLOR)
        stdout_rm, stderr_rm, retcode_rm = run_adb_command(
            ["shell", "rm", device_temp_path],
            command_name="Screenshot (Clean Up)",
            sync=True,
            display_output=False
        )
        if retcode_rm != 0:
            # This is often not critical, could be permission issue or file not found
            log_message(f"[WARN] Failed to remove temporary screenshot from device (Code: {retcode_rm}). May require manual removal.", WARN_COLOR)
            if stderr_rm: log_message(f"[STDERR] {stderr_rm}", WARN_COLOR)
        else:
            log_message("[ OK ] Temporary file removed from device.", OK_COLOR)


        # Final status message
        if success:
            log_message(f"[ OK ] Screenshot process completed. Saved to: {local_save_path}", OK_COLOR)
        else:
            log_message("[FAIL] Screenshot process failed. Check previous errors.", ERROR_COLOR)

    except Exception as e:
        log_message(f"[ERROR] Exception during screenshot process: {e}", ERROR_COLOR)
    finally:
        log_message("", tag_color=None) # Blank line


# --- Functions added in last step ---
def wake_sleep_device():
    """Simulates pressing the power button."""
    log_message("[INFO] Sending Power Key event (KEYCODE_POWER)...", INFO_COLOR)
    run_adb_command(["shell", "input", "keyevent", "KEYCODE_POWER"], command_name="Wake/Sleep Device")

def get_device_ip():
    """Attempts to get the device's primary IP address using 'ip route'."""
    log_message("[INFO] Attempting to get device IP (via ip route)... May not work on all configs.", INFO_COLOR)
    # Use sync=True to capture output directly if needed for future parsing
    # The pipe and awk make this a complex command needing careful handling by run_adb_command
    run_adb_command(
        ["shell", "ip", "route", "|", "awk", "'/src/ { print $9 }'"],
        command_name="Get Device IP Address",
        display_output=True # Show the result directly
    )
    # Note: The awk command might fail if awk isn't available or the output format is unexpected.

def list_device_features():
    """Lists hardware and software features declared by the device."""
    run_adb_command(["shell", "cmd", "package", "list", "features"], command_name="List Device Features")

def get_manufacturer():
    """Gets the device manufacturer name."""
    run_adb_command(["shell", "getprop", "ro.product.manufacturer"], command_name="Get Manufacturer")


def show_help():
    # Update help text version to match window title
    help_text = f"""
_______________________________________
         ADB Helper Commands (v1.1)
---------------------------------------
Category        Command        Description
------------    -------        -----------
**Connection & Server**
                List Devices   List connected devices and emulators (-l)
                Connect        Connect to device via IP (use IP:Port field)
                Disconnect     Disconnect device (use IP:Port field, or blank for all)
                Set TCP/IP     Restart ADB in TCP/IP mode on device (use Port field)
                Start Server   Start the ADB server on PC
                Kill Server    Kill the ADB server on PC
                Version        Show ADB's Version
                ADB Root       Restart ADB daemon with root permissions
                Remount Sys    Remount System Partition as R/W (requires root)

**Device Interaction**
                Start Shell    Start ADB shell in a new console window
                Screenshot     Take screenshot and save to PC
                Reboot         Reboot Device (Normal)
                Reboot BL      Reboot into Bootloader
                Reboot Rec     Reboot into Recovery
                Reboot FB      Reboot into Fastbootd (Userspace Fastboot)
                Wake/Sleep     Simulate Power Button press (toggle screen on/off)

**File Management**
                Push File      Push File (PC -> Device) - Select PC file, enter Device path
                Pull File      Pull File (Device -> PC) - Enter Device file path, select PC folder

**Application Management (Requires Package Name)**
                List Pkgs      List Installed Packages
                List Pkgs Path List Packages with File Locations
                List Pkgs 3rd  List only Third-Party Packages
                Install APK    Install APK - Select APK file (-r flag included)
                Uninstall APK  Uninstall APK
                Disable App    Disable App for current user (pm disable-user)
                Enable App     Enable a previously disabled App (pm enable)
                Clear Data     Clear App Data (Confirmation required)
                Force Stop     Force Stop App (am force-stop)

**Device Properties**
                Get Brightness Get current screen brightness (0-255)
                Set Brightness Set screen brightness (use Brightness field) [!] May need permission
                Get Serial     Get Device Serial Number
                Get Model      Get Device Model Name
                Get OS Ver     Get Android Version (e.g., 11, 12)
                Get Build      Get detailed Build Number/ID
                Get Battery    Get Battery Status (raw dumpsys battery output)
                Get Resolution Get Screen Resolution (raw wm size output)
                Get IP Addr    Attempt to get device's main IP address
                List Features  List device hardware/software features
                Get Mfr        Get Device Manufacturer Name

**Debugging & Logging**
                Start Logcat   Output device Logcat (streamed below, -v brief)
                Stop Logcat    Stops the Logcat stream

**GUI Controls**
                Clear Output   Clear this output text area
                Help           Show this help menu
_______________________________________
[!] = Note potential permission requirements or specific behavior.
"""
    log_message(help_text, INFO_COLOR) # Use log_message to display help in the text area


# --- GUI Setup ---
root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry(WINDOW_GEOMETRY)
root.config(bg=DEFAULT_BACKGROUND_COLOR)

# Set unified font
default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="Segoe UI", size=9) # Use a common modern font
root.option_add("*Font", default_font)
output_font = ("Consolas", 9) # Keep console font monospaced

# --- Style Configuration ---
style = ttk.Style()
try:
    # Try themes that generally look good on dark backgrounds
    available_themes = style.theme_names()
    theme_to_use = 'clam' if 'clam' in available_themes else ('alt' if 'alt' in available_themes else style.theme_use())
    if theme_to_use: style.theme_use(theme_to_use)
except tk.TclError:
    print("Default theme will be used.")

# Configure styles with our colors
style.configure("TButton", padding=5, relief="flat",
                background=BUTTON_BG, foreground=BUTTON_FG,
                font=('Segoe UI', 9, 'bold'))
style.map("TButton",
          background=[('active', '#6A6A6A'), ('disabled', '#555555')],
          foreground=[('active', BUTTON_FG), ('disabled', '#999999')])

style.configure("TLabel", padding=2, background=DEFAULT_BACKGROUND_COLOR, foreground=LABEL_FG, font=('Segoe UI', 9))
style.configure("TEntry", padding=(5, 3), fieldbackground=ENTRY_BG, foreground=ENTRY_FG, insertcolor=ENTRY_FG) # Adjusted padding
style.configure("TFrame", background=DEFAULT_BACKGROUND_COLOR)


# --- Main Container Frame ---
main_frame = ttk.Frame(root, padding="10 10 10 10", style="TFrame")
main_frame.pack(expand=True, fill=tk.BOTH)


# --- Input Frame ---
input_frame = ttk.Frame(main_frame, padding="5", style="TFrame")
input_frame.pack(fill=tk.X, pady=(0, 10)) # Add padding below
input_frame.columnconfigure(1, weight=1) # Allow entry fields to expand

row_idx = 0
# IP Address
ip_label = ttk.Label(input_frame, text="IP:Port")
ip_label.grid(row=row_idx, column=0, padx=5, pady=3, sticky="w")
ip_entry = ttk.Entry(input_frame, width=25)
ip_entry.grid(row=row_idx, column=1, padx=5, pady=3, sticky="ew", columnspan=2)
# TCP/IP Port (moved next to IP)
port_label = ttk.Label(input_frame, text="TCP Port:")
port_label.grid(row=row_idx, column=3, padx=(15,5), pady=3, sticky="e")
port_entry = ttk.Entry(input_frame, width=8)
port_entry.grid(row=row_idx, column=4, padx=5, pady=3, sticky="w")
row_idx += 1

# Package Name
package_label = ttk.Label(input_frame, text="Package Name")
package_label.grid(row=row_idx, column=0, padx=5, pady=3, sticky="w")
package_name_entry = ttk.Entry(input_frame, width=40)
package_name_entry.grid(row=row_idx, column=1, padx=5, pady=3, sticky="ew", columnspan=4)
row_idx += 1

# Brightness
brightness_label = ttk.Label(input_frame, text="Brightness (0-255)")
brightness_label.grid(row=row_idx, column=0, padx=5, pady=3, sticky="w")
brightness_entry = ttk.Entry(input_frame, width=10)
brightness_entry.grid(row=row_idx, column=1, padx=5, pady=3, sticky="w")
row_idx += 1

# Device Path (Push)
device_path_label_push = ttk.Label(input_frame, text="Device Path (Push)")
device_path_label_push.grid(row=row_idx, column=0, padx=5, pady=3, sticky="w")
device_path_entry_push = ttk.Entry(input_frame, width=40)
device_path_entry_push.grid(row=row_idx, column=1, padx=5, pady=3, sticky="ew", columnspan=4)
device_path_entry_push.insert(0, "/sdcard/Download/") # Default value
row_idx += 1

# Device Path (Pull)
device_path_label_pull = ttk.Label(input_frame, text="Device Path (Pull)")
device_path_label_pull.grid(row=row_idx, column=0, padx=5, pady=3, sticky="w")
device_path_entry_pull = ttk.Entry(input_frame, width=40)
device_path_entry_pull.grid(row=row_idx, column=1, padx=5, pady=3, sticky="ew", columnspan=4)
row_idx += 1


# --- Button Frame ---
button_frame = ttk.Frame(main_frame, padding="5", style="TFrame")
button_frame.pack(fill=tk.X, pady=5)

num_cols = 7 # Increased columns to fit more buttons neatly
for i in range(num_cols):
    button_frame.columnconfigure(i, weight=1)

# Group buttons logically
buttons = [
    # Row 1: Connection / Server / Basic Info
    ("List Devices", list_devices), ("Connect", connect_device), ("Disconnect", disconnect_device),
    ("Set TCP/IP", set_tcpip_mode), ("Start Server", start_server), ("Kill Server", kill_server), ("Version", show_version),
    # Row 2: Device Interaction / Reboot
    ("Start Shell", start_shell), ("Screenshot", take_screenshot), ("Reboot", lambda: reboot_device()),
    ("Reboot BL", lambda: reboot_device("bootloader")), ("Reboot Rec", lambda: reboot_device("recovery")), ("Reboot FB", lambda: reboot_device("fastboot")), ("ADB Root", root_adb),
    # Row 3: File Management / System
    ("Push File", push_file), ("Pull File", pull_file), ("Remount Sys", remount_system),
     ("Get Serial", get_serial_number), ("Get Model", get_device_model), ("Get OS Ver", get_android_version),("Get Build", get_build_number),
    # Row 4: Device Properties
    ("Get Brightness", get_brightness), ("Set Brightness", set_brightness), ("Get Battery", get_battery_status),
    ("Get Resolution", get_screen_resolution), ("Help", show_help), ("Clear Output", clear_output), ("Wake/Sleep", wake_sleep_device), # <<<--- FILLED SLOT
    # Row 5: App Management
    ("List Pkgs", lambda: list_packages(False, False)), ("List Pkgs Path", lambda: list_packages(True, False)), ("List Pkgs 3rd", lambda: list_packages(False, True)),
    ("Install APK", install_apk), ("Uninstall APK", uninstall_apk), ("Clear Data", clear_app_data), ("Force Stop", force_stop_app),
    # Row 6: App Management / Logcat / Misc Info
    ("Disable App", lambda: toggle_app(False)), ("Enable App", lambda: toggle_app(True)), ("Start Logcat", start_logcat),
    ("Stop Logcat", stop_logcat), ("Get IP Addr", get_device_ip), ("List Features", list_device_features), ("Get Mfr", get_manufacturer) # <<<--- FILLED SLOTS
]

r, c = 0, 0
for text, cmd in buttons:
    if text is None: # Skip placeholders
        pass
    else:
        # Reduce padding slightly if needed, or adjust width
        btn = ttk.Button(button_frame, text=text, command=cmd, width=13, style="TButton") # Slightly reduced width maybe
        btn.grid(row=r, column=c, padx=2, pady=2, sticky="ew")

    c += 1
    if c >= num_cols:
        c = 0
        r += 1

# --- Output Text Area ---
output_frame = ttk.Frame(main_frame, padding=(5, 0, 5, 5), style="TFrame") # Pad top=0
output_frame.pack(expand=True, fill=tk.BOTH, pady=5)

output_text = scrolledtext.ScrolledText(
    output_frame,
    wrap=tk.WORD,
    state=tk.DISABLED,
    bg=TEXT_AREA_BG,
    fg=TEXT_AREA_FG,
    font=output_font, # Use specific output font
    padx=5, # Add padding inside the text area
    pady=5,
    relief=tk.FLAT, # Match entry style
    borderwidth=1 # Subtle border like entry
)
# Configure tags for colors (can be done once)
output_text.tag_config(f"color_{INFO_COLOR.replace('#', '')}", foreground=INFO_COLOR)
output_text.tag_config(f"color_{OK_COLOR.replace('#', '')}", foreground=OK_COLOR)
output_text.tag_config(f"color_{WARN_COLOR.replace('#', '')}", foreground=WARN_COLOR)
output_text.tag_config(f"color_{ERROR_COLOR.replace('#', '')}", foreground=ERROR_COLOR)
output_text.tag_config(f"color_{EXEC_COLOR.replace('#', '')}", foreground=EXEC_COLOR)
output_text.pack(expand=True, fill=tk.BOTH)


# --- Initial Actions ---
def initialize_app():
    global adb_executable_path
    adb_found = find_adb_path()

    # Disable all command buttons initially if ADB not found
    if not adb_found:
        for child in button_frame.winfo_children():
            if isinstance(child, ttk.Button):
                 # Keep Help and Clear Output enabled
                 if child.cget('text') not in ["Help", "Clear Output"]:
                    child.configure(state=tk.DISABLED)

    log_message(f"{WINDOW_TITLE} Initialized.", INFO_COLOR)
    log_message(f"Platform: {sys.platform}", INFO_COLOR)
    if adb_executable_path:
         log_message(f"Using ADB: {adb_executable_path}", INFO_COLOR)
    else:
         log_message("[WARN] ADB not found. Most commands are disabled.", WARN_COLOR)
         log_message("[WARN] Ensure ADB is in your PATH or standard SDK locations.", WARN_COLOR)
    log_message("-----------------------------------------------------", INFO_COLOR)
    log_message("Enter details above and click command buttons.", INFO_COLOR)
    log_message("Click 'Help' for command details.", INFO_COLOR)

# Run initialization after the main loop starts to ensure widgets exist
root.after(100, initialize_app)

# --- Graceful Shutdown ---
def on_closing():
    global logcat_process, is_stopping_logcat
    if logcat_process and logcat_process.poll() is None:
        log_message("[INFO] Stopping active Logcat before exit...", INFO_COLOR)
        is_stopping_logcat = True # Set flag
        proc_to_stop = logcat_process
        logcat_process = None # Signal thread
        try:
            proc_to_stop.terminate()
            proc_to_stop.wait(timeout=0.5) # Brief wait
        except Exception:
            pass # Ignore errors on close
    # Ensure GUI closes even if logcat stop fails
    try:
        root.destroy()
    except tk.TclError:
        pass # Ignore if already destroyed

root.protocol("WM_DELETE_WINDOW", on_closing)

# --- Start GUI ---
root.mainloop()