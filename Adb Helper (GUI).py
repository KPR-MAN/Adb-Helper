import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, font
import subprocess
import os
import sys
import shutil
import threading
# PIL/ImageTk imports are already removed

# --- Configuration ---
WINDOW_TITLE = "ADB Helper GUI" # <<<--- Title remains
WINDOW_GEOMETRY = "800x700"
DEFAULT_BACKGROUND_COLOR = "#2E2E2E" # Dark gray background remains
TEXT_AREA_BG = "#1E1E1E" # Darker background for text
TEXT_AREA_FG = "#DCDCDC" # Light gray text
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

# --- ADB Path Detection ---
# (find_adb_path function remains the same)
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
        local_appdata = os.getenv('LOCALAPPDATA')
        if local_appdata:
            default_sdk_path = os.path.join(local_appdata, "Android", "Sdk", "platform-tools", adb_exe)
            if os.path.exists(default_sdk_path):
                adb_executable_path = default_sdk_path
                log_message(f"[INFO] Found ADB in default SDK location: {adb_executable_path}", INFO_COLOR)
                return adb_executable_path

        # 3. Fallback (Update this if needed)
        fallback_path = os.path.join(os.getenv('USERPROFILE', ''), "AppData", "Local", "Android", "Sdk", "platform-tools", adb_exe)
        if os.path.exists(fallback_path):
             adb_executable_path = fallback_path
             log_message(f"[WARN] Using fallback ADB path: {adb_executable_path}", WARN_COLOR)
             return adb_executable_path

    # Add more checks for Linux/macOS if needed here
    # e.g., ~/Android/Sdk/platform-tools/adb

    log_message("[ERROR] ADB executable not found.", ERROR_COLOR)
    log_message("[ERROR] Please ensure ADB is installed and in your PATH or update search paths in the script.", ERROR_COLOR)
    messagebox.showerror("ADB Not Found", "Could not locate adb.exe. Please ensure it's installed and in your PATH.")
    return None


# --- Helper Functions ---
# (run_adb_command and log_message functions remain the same)
def run_adb_command(args, display_output=True, command_name="Command"):
    """Executes an ADB command in a separate thread and logs output."""
    if not adb_executable_path:
        log_message("[ERROR] ADB path not set. Cannot run command.", ERROR_COLOR)
        return

    # Construct the command list
    command = [adb_executable_path] + args

    log_message(f"\n[EXEC] {' '.join(command)}", EXEC_COLOR)

    def command_thread():
        global logcat_process
        try:
            # Use Popen for potentially long-running commands or when needing process control
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0 # Hide console window on Windows
            )

            # Special handling for logcat
            if args and args[0] == 'logcat' and args[-1] != '-d': # '-d' dumps logcat and exits
                logcat_process = process
                # Stream output for logcat
                log_message(f"[ OK ] {command_name} started. Streaming output... (Use 'Stop Logcat')", OK_COLOR)
                # Read line by line to show live output
                for line in iter(process.stdout.readline, ''):
                    # Check if stop was requested *before* trying to log
                    if logcat_process != process:
                        log_message("[INFO] Logcat stop requested, halting output.", INFO_COLOR)
                        break
                    log_message(line.strip(), TEXT_AREA_FG) # Use default text color for log content

                process.stdout.close()
                # Ensure process termination if stop was requested mid-stream
                if logcat_process != process and process.poll() is None:
                    process.terminate()

                return_code = process.wait() # Wait for process to finish naturally or after terminate
                stderr_output = process.stderr.read()

                # Check if the logcat_process is None *after* wait() to confirm it was stopped externally
                if logcat_process is None:
                    log_message(f"[INFO] Logcat stream stopped (Code: {return_code}).", INFO_COLOR)
                else: # Finished naturally
                    logcat_process = None # Clear the global process tracker
                    log_message(f"[INFO] Logcat stream ended naturally (Code: {return_code}).", INFO_COLOR)

                if stderr_output:
                        log_message(f"[STDERR]\n{stderr_output.strip()}", WARN_COLOR)

            else: # For other commands
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
            log_message(f"[ERROR] ADB executable not found at: {adb_executable_path}", ERROR_COLOR)
        except Exception as e:
            log_message(f"[ERROR] Failed to execute ADB command: {e}", ERROR_COLOR)
        finally:
             log_message("") # Add a blank line for spacing

    # Start the command execution in a separate thread
    thread = threading.Thread(target=command_thread, daemon=True)
    thread.start()

def log_message(message, tag_color=None):
    """Appends a message to the text area, applying color if specified."""
    try:
        output_text.config(state=tk.NORMAL)
        if tag_color:
            # Create a tag for the color if it doesn't exist
            tag_name = f"color_{tag_color.replace('#', '')}"
            if tag_name not in output_text.tag_names():
                 output_text.tag_config(tag_name, foreground=tag_color)
            output_text.insert(tk.END, message + "\n", tag_name)
        else:
            output_text.insert(tk.END, message + "\n")
        output_text.see(tk.END) # Scroll to the end
        output_text.config(state=tk.DISABLED)
        # Schedule an update to ensure the GUI remains responsive
        root.update_idletasks()
    except tk.TclError as e:
        pass
    except Exception as e:
        pass


# --- Specific Command Functions ---
# (These functions remain the same as before)
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
        if sys.platform == "win32":
            subprocess.Popen(['cmd.exe', '/c', 'start', 'cmd.exe', '/k', f'"{adb_executable_path}" shell'])
        else:
             log_message("[INFO] Attempting to open shell in default terminal (Linux/macOS)...", INFO_COLOR)
             terminals = ['x-terminal-emulator', 'gnome-terminal', 'konsole', 'xfce4-terminal', 'lxterminal', 'mate-terminal']
             cmd = f"'{adb_executable_path}' shell"
             opened = False
             for term in terminals:
                 try:
                     subprocess.Popen([term, '-e', cmd])
                     opened = True
                     break
                 except FileNotFoundError:
                     continue
             if not opened:
                 if sys.platform == "darwin":
                    try:
                        subprocess.Popen(['open', '-a', 'Terminal', adb_executable_path, 'shell'])
                        opened = True
                    except FileNotFoundError:
                        pass
                    except Exception as e_mac:
                        log_message(f"[WARN] Failed to open macOS Terminal: {e_mac}", WARN_COLOR)

             if not opened:
                  log_message("[ERROR] Could not find a known terminal emulator to start shell automatically.", ERROR_COLOR)
                  raise Exception("No suitable terminal found")

    except Exception as e:
        log_message(f"[ERROR] Could not open shell in new window: {e}", ERROR_COLOR)
        log_message("[INFO] Trying direct execution (output might be limited here).", INFO_COLOR)
        run_adb_command(["shell"], command_name="Start Shell (Direct)", display_output=True) # Fallback

def push_file():
    local_path = filedialog.askopenfilename(title="Select File to Push (PC)")
    if not local_path: return
    device_path = device_path_entry_push.get()
    if not device_path:
        device_path = "/sdcard/Download/" # Default if empty
        log_message(f"[INFO] No device path specified, using default: {device_path}", INFO_COLOR)
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
    run_adb_command(["install", apk_path], command_name="Install APK")

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
    run_adb_command(command, command_name=cmd_name)

def root_adb():
    run_adb_command(["root"], command_name="Restart ADB as Root")

def remount_system():
    run_adb_command(["remount"], command_name="Remount System")

def list_packages(show_paths=False):
    command = ["shell", "pm", "list", "packages"]
    cmd_name = "List Packages"
    if show_paths:
        command.append("-f")
        cmd_name = "List Packages with Paths"
    run_adb_command(command, command_name=cmd_name)

def toggle_app(enable=True):
    package_name = package_name_entry.get()
    if not package_name:
        log_message("[WARN] Please enter the package name.", WARN_COLOR)
        return
    action = "enable" if enable else "disable-user"
    command = ["shell", "pm", action]
    # disable-user often requires specifying the user
    if not enable:
         command.extend(["--user", "0"])
    command.append(package_name)
    cmd_name = f"{'Enable' if enable else 'Disable'} App"
    run_adb_command(command, command_name=cmd_name)

def start_logcat():
    global logcat_process
    if logcat_process and logcat_process.poll() is None:
        log_message("[WARN] Logcat is already running.", WARN_COLOR)
        return
    # Reset just in case the variable holds a finished process handle
    logcat_process = None
    # Run logcat without '-d' to keep it streaming
    run_adb_command(["logcat"], command_name="Start Logcat", display_output=False)

def stop_logcat():
    global logcat_process
    if logcat_process and logcat_process.poll() is None: # Check if process exists and is running
        log_message("[INFO] Attempting to stop Logcat...", INFO_COLOR)
        try:
            # Signal the reading thread to stop by setting logcat_process to None
            proc_to_stop = logcat_process
            logcat_process = None # Signal thread first
            proc_to_stop.terminate() # Then terminate the process
            # Give terminate a moment, then kill if needed (optional)
            try:
                proc_to_stop.wait(timeout=0.5) # Check if terminate worked quickly
            except subprocess.TimeoutExpired:
                log_message("[WARN] Logcat did not terminate gracefully, attempting kill...", WARN_COLOR)
                proc_to_stop.kill() # Force kill
                proc_to_stop.wait(timeout=1) # Wait briefly for kill

            # Check again if it's really stopped
            if proc_to_stop.poll() is not None:
                 log_message("[ OK ] Logcat process stopped.", OK_COLOR)
            else:
                 log_message("[ERROR] Failed to stop the Logcat process.", ERROR_COLOR)
                 logcat_process = proc_to_stop # Put it back if stop failed? Maybe not helpful.

        except Exception as e:
            log_message(f"[ERROR] Failed to stop Logcat process: {e}", ERROR_COLOR)
            # Ensure logcat_process is None if an error occurred during stop attempt
            logcat_process = None
    else:
        log_message("[INFO] Logcat is not running or already stopped.", INFO_COLOR)
        logcat_process = None # Ensure it's cleared

def clear_output():
    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.config(state=tk.DISABLED)

def show_help():
    help_text = """
_______________________________________
         ADB Helper Commands
---------------------------------------
Command        Description
-------        -----------
Connect        Connect to device via IP (enter IP:Port below)
Disconnect     Disconnect device (enter IP:Port below, or blank for all)
Set TCP/IP     Restart ADB in TCP/IP mode on device (enter Port below)
Start Server   Start the ADB server on PC
Kill Server    Kill the ADB server on PC
Version        Show ADB's Version
Start Shell    Start ADB shell in a new console window
Push File      Push File (PC -> Device) - Select PC file, enter Device path
Pull File      Pull File (Device -> PC) - Enter Device file path, select PC folder
Install APK    Install APK - Select APK file
Uninstall APK  Uninstall APK (enter Package Name below)
Reboot         Reboot Device (Normal)
Reboot BL      Reboot into Bootloader
Reboot Rec     Reboot into Recovery
ADB Root       Restart ADB daemon with root permissions
Remount Sys    Remount System Partition (requires root)
List Pkgs      List Installed Packages
List Pkgs Path List Packages with File Locations
Disable App    Disable App (enter Package Name below)
Enable App     Enable App (enter Package Name below)
Start Logcat   Output device Logcat (streamed below)
Stop Logcat    Stops the Logcat stream
Clear Output   Clear this output area
Help           Shows this help menu
_______________________________________
"""
    log_message(help_text, INFO_COLOR)


# --- GUI Setup ---
root = tk.Tk()
root.title(WINDOW_TITLE) # <<<--- Set the window title
root.geometry(WINDOW_GEOMETRY)

# --- Set Background Color for the main window ---
root.config(bg=DEFAULT_BACKGROUND_COLOR)

# --- NO ICON SETTING CODE HERE ---

# Set unified font
default_font = font.nametofont("TkDefaultFont")
default_font.configure(size=10)
root.option_add("*Font", default_font)

# --- Style Configuration ---
style = ttk.Style()
try:
    style.theme_use('clam')
except tk.TclError:
    print("Clam theme not available, using default.")

# Configure styles with background colors
style.configure("TButton", padding=6, relief="flat",
                background=BUTTON_BG, foreground=BUTTON_FG,
                font=('Helvetica', 9, 'bold'))
style.map("TButton",
          background=[('active', '#6A6A6A')],
          foreground=[('active', BUTTON_FG)])

style.configure("TLabel", padding=2, background=DEFAULT_BACKGROUND_COLOR, foreground=LABEL_FG, font=('Helvetica', 9))
style.configure("TEntry", padding=5, fieldbackground=ENTRY_BG, foreground=ENTRY_FG, insertcolor=ENTRY_FG)
style.configure("TFrame", background=DEFAULT_BACKGROUND_COLOR)

# --- Main Container Frame ---
main_frame = ttk.Frame(root, padding="10 10 10 10", style="TFrame")
main_frame.pack(expand=True, fill=tk.BOTH)


# --- Input Frame ---
input_frame = ttk.Frame(main_frame, padding="5", style="TFrame")
input_frame.pack(fill=tk.X, pady=5)
input_frame.columnconfigure(1, weight=1)

row_idx = 0
# IP Address
ip_label = ttk.Label(input_frame, text="IP:Port")
ip_label.grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
ip_entry = ttk.Entry(input_frame, width=30)
ip_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
row_idx += 1

# Port
port_label = ttk.Label(input_frame, text="TCP/IP Port")
port_label.grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
port_entry = ttk.Entry(input_frame, width=10)
port_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
row_idx += 1

# Package Name
package_label = ttk.Label(input_frame, text="Package Name")
package_label.grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
package_name_entry = ttk.Entry(input_frame, width=40)
package_name_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
row_idx += 1

# Device Path (Push)
device_path_label_push = ttk.Label(input_frame, text="Device Path (Push)")
device_path_label_push.grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
device_path_entry_push = ttk.Entry(input_frame, width=40)
device_path_entry_push.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
device_path_entry_push.insert(0, "/sdcard/Download/") # Default value
row_idx += 1

# Device Path (Pull)
device_path_label_pull = ttk.Label(input_frame, text="Device Path (Pull)")
device_path_label_pull.grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
device_path_entry_pull = ttk.Entry(input_frame, width=40)
device_path_entry_pull.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
row_idx += 1


# --- Button Frame ---
button_frame = ttk.Frame(main_frame, padding="5", style="TFrame")
button_frame.pack(fill=tk.X, pady=5)

num_cols = 6
for i in range(num_cols):
    button_frame.columnconfigure(i, weight=1)

buttons = [
    ("Connect", connect_device), ("Disconnect", disconnect_device), ("Set TCP/IP", set_tcpip_mode),
    ("Start Server", start_server), ("Kill Server", kill_server), ("Version", show_version),
    ("Start Shell", start_shell), ("Push File", push_file), ("Pull File", pull_file),
    ("Install APK", install_apk), ("Uninstall APK", uninstall_apk), ("Reboot", lambda: reboot_device()),
    ("Reboot BL", lambda: reboot_device("bootloader")), ("Reboot Rec", lambda: reboot_device("recovery")), ("ADB Root", root_adb),
    ("Remount Sys", remount_system), ("List Pkgs", lambda: list_packages(False)), ("List Pkgs Path", lambda: list_packages(True)),
    ("Disable App", lambda: toggle_app(False)), ("Enable App", lambda: toggle_app(True)), ("Start Logcat", start_logcat),
    ("Stop Logcat", stop_logcat), ("Clear Output", clear_output), ("Help", show_help)
]

r, c = 0, 0
for text, cmd in buttons:
    btn = ttk.Button(button_frame, text=text, command=cmd, width=15)
    btn.grid(row=r, column=c, padx=3, pady=3, sticky="ew")
    c += 1
    if c >= num_cols:
        c = 0
        r += 1

# --- Output Text Area ---
output_frame = ttk.Frame(main_frame, padding="5", style="TFrame")
output_frame.pack(expand=True, fill=tk.BOTH, pady=5)

output_text = scrolledtext.ScrolledText(
    output_frame,
    wrap=tk.WORD,
    state=tk.DISABLED,
    bg=TEXT_AREA_BG,
    fg=TEXT_AREA_FG,
    font=("Consolas", 9)
)
output_text.pack(expand=True, fill=tk.BOTH)

# --- Initial Actions ---
adb_found = find_adb_path()
if not adb_found:
    for child in button_frame.winfo_children():
        if isinstance(child, ttk.Button):
             child.configure(state=tk.DISABLED)

log_message("ADB Helper GUI Initialized.", INFO_COLOR)
log_message(f"Platform: {sys.platform}", INFO_COLOR)
if adb_executable_path:
     log_message(f"Using ADB: {adb_executable_path}", INFO_COLOR)
else:
     log_message("[WARN] ADB not found. Most commands will fail.", WARN_COLOR)
log_message("Enter details above and click command buttons.", INFO_COLOR)
log_message("Click 'Help' for command details.", INFO_COLOR)


# --- Start GUI ---
root.mainloop()