import tkinter as tk
import ttkbootstrap as ttk
import main, subprocess, time, os, importlib, pickle, webbrowser, sys
from PIL import Image, ImageTk
from functools import partial
from tkinter import filedialog

is_settings_window_open = False
file_name = "ahk_manager_config.txt"
data = {}

def resource_path(relative_path):
    # Get absolute path to a resource for pyinstaller
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def save_data():
    with open(file_name, 'wb') as file:
        pickle.dump(data, file)

def load_data():
    global ahk_path
    try:
        with open(file_name, 'rb') as file:
            data = pickle.load(file)
    except FileNotFoundError:
        print("File was not found")
    except Exception:
        pass
    for x in data:
        match x:
            case 'path':
                ahk_path = data["path"]
        


# check if file doesn't exists
if not os.path.isfile(file_name):
    # ahk path that is set on first launch and can be configured in settings
    ahk_path = "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe"
    data["path"] = ahk_path
    save_data()
else:
    load_data()

def settings_window():
    global is_settings_window_open
    if not is_settings_window_open:
        is_settings_window_open = True
        settings_window = ttk.Toplevel(window, resizable=(False, False))
        settings_window.title("Settings")
        settings_window.geometry("650x530")
        settings_window.attributes("-topmost", True)
        settings_window.iconbitmap(resource_path(os.path.join("assets","icon.ico")))
        # place the window in the middle of the screen
        settings_window.wait_visibility()
        x = window.winfo_x() + window.winfo_width()//2 - settings_window.winfo_width()//2
        y = window.winfo_y() + window.winfo_height()//2 - settings_window.winfo_height()//2
        settings_window.geometry(f"+{x}+{y-60}")

        # window closing
        settings_window_close = partial(settings_window_closed, settings_window)
        settings_window.protocol("WM_DELETE_WINDOW", settings_window_close)

        # labels
        settings_label = ttk.Label(settings_window, text="Settings", font='Calibri 40 bold')
        settings_label.pack()
        ttk.Label(settings_window, text="Auto Hotkey Executable Path", font='Calibri 20').pack(pady=(0,10))

        # path settings
        path_frame = ttk.Frame(master=settings_window)
        # entry
        global filepath_text
        filepath_text = ttk.StringVar()
        filepath_text.trace_add("write", on_filepath_change)
        filepath_entry = ttk.Entry(master=path_frame, textvariable=filepath_text, width=65, font="Calibri 12")
        filepath_entry.insert(0, ahk_path)
        filepath_entry.grid(row=0, column=0, sticky=tk.W + tk.N + tk.S)
        # button
        select_file = partial(file_dialog,settings_window)
        filepath_button = ttk.Button(master=path_frame, image=file_dialog_image, command=select_file)
        filepath_button.grid(row=0, column=2, sticky=tk.E, padx=(20,0), pady=(0,0))
        # frame
        path_frame.pack(fill=tk.NONE, expand=False, padx=10, pady=(5,20))
        path_frame.grid_rowconfigure(0, weight=1)  # Allow the row to expand vertically
        path_frame.grid_columnconfigure(0, weight=1) # Allow column 0 to expand
        path_frame.grid_columnconfigure(1, weight=1) # Allow column 1 (spacer) to expand
        path_frame.grid_columnconfigure(2, weight=1) # Allow column 2 to expand

        ttk.Label(settings_window, text="Make sure this is the correct path to Auto Hotkey or else the program \nwill not be able to restart or launch any scripts", font='Calibri 14', justify=tk.CENTER).pack()
        madeby_label = ttk.Label(settings_window, text="Made by smeks", foreground="#dff9ff", font='Calibri 13', justify=tk.CENTER)
        madeby_label.pack(pady=(270,0))
        madeby_label.bind("<Button-1>", lambda e: print(""))

def open_url(url):
    webbrowser.open_new(url)

def on_filepath_change(*args):
    global ahk_path
    ahk_path = filepath_text.get()
    data["path"] = ahk_path
    save_data()

def file_dialog(settings_window):
    global ahk_path
    settings_window.withdraw()
    initialdir_c = ""
    for x in ahk_path.split("\\"):
        if x != ahk_path.split("\\")[-1]:
            initialdir_c += x + "\\"
    filepath = filedialog.askopenfile(
        initialdir=initialdir_c,
        title="Select Auto Hotkey executable",
        filetypes=(("EXE files","*.exe"), ("All files", "*.*"))
    )
    if filepath:
        print(filepath)
        settings_window.deiconify()
        ahk_path = filepath.name
        data["path"] = ahk_path
        save_data()
        return filepath
    settings_window.deiconify()

    

def settings_window_closed(settings_window):
    global is_settings_window_open
    is_settings_window_open = False
    settings_window.destroy()
    # SAVE PATH

# ToolTip object for mouse over on buttons
class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self,text):
        # Display text in tooltip window
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x+= self.widget.winfo_rootx()+40
        y+= cy+self.widget.winfo_rooty()+20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = ttk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#201D1D", relief=tk.SOLID, borderwidth=1,
                      font=("Calibri", "15", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    def CreateToolTip(widget, text):
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)


killed_scripts = []


# opens the notepad to a script
def edit_script(path):
    subprocess.run(["notepad",os.path.expandvars(path)])

# restarts a script, then rescans scripts
def restart_script(path,pid):
    subprocess.run(["taskkill","/PID",str(pid)])
    subprocess.Popen([os.path.join(ahk_path),os.path.join(path)])
    time.sleep(0.1)
    re_scan_scripts()

# runs a scripts, then removes it from killed scripts, and then rescans scripts
def run_script(path,script):
    global killed_scripts
    killed_scripts.pop(killed_scripts.index(script))
    subprocess.Popen([os.path.join(ahk_path),os.path.join(path)])
    time.sleep(0.1)
    re_scan_scripts()

# kills scripts as well as rescanning them
def kill_script(pid,script):
    global killed_scripts
    killed_scripts.append(script)
    subprocess.run(["taskkill","/PID",str(pid)])
    time.sleep(0.1)
    re_scan_scripts()

# this function deletes every widget related to scripts and basically starts the program from scratch again
def re_scan_scripts():
    for frame in individual_script_frames:
        widgets = frame.grid_slaves()
        for widget in widgets:
            widget.destroy()
        frame.destroy()
    time.sleep(0.1)
    importlib.reload(main)
    ahk_scripts = main.ahk_scripts
    ahk_scripts_tk(ahk_scripts)
        


def ahk_scripts_tk(ahk_scripts_func):
    all_scripts = []
    all_scripts_frames = []
    # loop for every RUNNING script and include it's name and path 
    for script in ahk_scripts_func:
        edit_button = partial(edit_script, script.get("path"))
        restart_button = partial(restart_script, script.get("path"), script.get("pid"))
        stop_process_button = partial(kill_script, script.get("pid"), script)
        all_scripts_frames.append(ttk.Frame(master=scripts_frame, width=960, height=50, style='TFrame'))
        all_scripts.append([
            ttk.Label(master=all_scripts_frames[ahk_scripts_func.index(script)],text=script.get("script_name"), font='Calibri 27', style='TLabel'), 
            ttk.Label(master=all_scripts_frames[ahk_scripts_func.index(script)],text=script.get("path"), font='Calibri 12', style='TLabel'),
            ttk.Button(master=all_scripts_frames[ahk_scripts_func.index(script)], image=edit_image, style='My.TButton', command=edit_button),
            ttk.Button(master=all_scripts_frames[ahk_scripts_func.index(script)], image=restart_image, style='My.TButton', command=restart_button),
            ttk.Button(master=all_scripts_frames[ahk_scripts_func.index(script)], image=stop_process_image, style='My.TButton', command=stop_process_button)
            ])
    # loop for every KILLED script and include it's name and path AND set the background color to red
    for script in killed_scripts:
        print(script.get("pid"),"\n",script.get("path"))
        # manually add a run button to killed scripts
        run_button = partial(run_script, script.get("path"), script)
        all_scripts_frames.append(ttk.Frame(master=scripts_frame, width=960, height=50, style='Red.TFrame'))
        run_button_temp = ttk.Button(master=all_scripts_frames[killed_scripts.index(script)+len(ahk_scripts_func)], image=run_image, style='My.TButton', command=run_button)
        run_button_temp.grid(row=0, column=1, sticky="w", padx=10, pady=0)
        ToolTip.CreateToolTip(run_button_temp, text = "Run killed script")

        all_scripts.append([
            ttk.Label(master=all_scripts_frames[killed_scripts.index(script)+len(ahk_scripts_func)],text=script.get("script_name"), font='Calibri 27', style='Red.TLabel'),
            ttk.Label(master=all_scripts_frames[killed_scripts.index(script)+len(ahk_scripts_func)],text=script.get("path"), font='Calibri 12', style='Red.TLabel')
            ])

    # grid ALL of the ahk script related elements

    for x in range(len(all_scripts)):
        for y in range(len(all_scripts[x])):
            match y:
                case 0: # Name Label
                    all_scripts[x][y].grid(row=0, column=0, sticky="w", padx=10, pady=0)
                case 1: # Path
                   all_scripts[x][y].grid(row=1, column=0, sticky="w", padx=10, pady=(0,40))
                case 2: # Edit Button
                    all_scripts[x][y].grid(row=0, column=1, sticky="w", padx=10, pady=0)
                    ToolTip.CreateToolTip(all_scripts[x][y], text = "Edit script")
                case 3: # Restart script button
                    all_scripts[x][y].grid(row=0, column=2, sticky="w", padx=10, pady=0)
                    ToolTip.CreateToolTip(all_scripts[x][y], text = "Restart script")
                case 4: # Kill script button
                    all_scripts[x][y].grid(row=0, column=3, sticky="w", padx=10, pady=0)    
                    ToolTip.CreateToolTip(all_scripts[x][y], text = "Kill script")


        all_scripts_frames[x].grid_columnconfigure(0, weight=1)
        all_scripts_frames[x].grid_columnconfigure(1, weight=0)
        all_scripts_frames[x].pack(fill="both", expand=True, side="top")
        global individual_script_frames
        individual_script_frames = all_scripts_frames
    return

# window & style
window = ttk.Window(resizable=(False, False))
ttk.Style().load_user_themes(resource_path("ttkb_themes.json"))
ttk.Style().theme_use("ahk")
window.title("Auto Hotkey Scripts Manager")
window.geometry('960x800')
# icon
icon_path = resource_path(os.path.join("assets","icon.ico"))
window.iconbitmap(icon_path)

# images
edit_image_c = Image.open(resource_path(os.path.join("assets","edit.png"))).resize((20,20), Image.Resampling.LANCZOS)
edit_image = ImageTk.PhotoImage(edit_image_c)
restart_image_c = Image.open(resource_path(os.path.join("assets","restart.png"))).resize((20,20), Image.Resampling.LANCZOS)
restart_image = ImageTk.PhotoImage(restart_image_c)
stop_process_image_c = Image.open(resource_path(os.path.join("assets","stop_process.png"))).resize((20,20), Image.Resampling.LANCZOS)
stop_process_image = ImageTk.PhotoImage(stop_process_image_c)
settings_image_c = Image.open(resource_path(os.path.join("assets","settings.png"))).resize((20,20), Image.Resampling.LANCZOS)
settings_image = ImageTk.PhotoImage(settings_image_c)
run_image_c = Image.open(resource_path(os.path.join("assets","run.png"))).resize((20,20), Image.Resampling.LANCZOS)
run_image = ImageTk.PhotoImage(run_image_c)
file_dialog_image_c = Image.open(resource_path(os.path.join("assets","file_dialog.png"))).resize((20,20), Image.Resampling.LANCZOS)
file_dialog_image = ImageTk.PhotoImage(file_dialog_image_c)

# ahk scripts
ahk_scripts = main.ahk_scripts

# title label & frame
title_frame = ttk.Frame(master=window, width=380, height=180)
title_label = ttk.Label(master=title_frame, font='Calibri 40 bold', text="Auto HotKey Scripts Manager")
title_label.grid(row=0, column=0, sticky=tk.W + tk.N + tk.S)

# settings
settings_button = ttk.Button(master=title_frame, image=settings_image, command=settings_window)
settings_button.grid(row=0, column=2, sticky=tk.E, padx=(100,0), pady=(10,0))
ToolTip.CreateToolTip(settings_button, text = "Settings")


title_frame.pack(fill=tk.NONE, expand=False, padx=10, pady=(5,20))
title_frame.grid_rowconfigure(0, weight=1)  # Allow the row to expand vertically
title_frame.grid_columnconfigure(0, weight=1) # Allow column 0 to expand
title_frame.grid_columnconfigure(1, weight=1) # Allow column 1 (spacer) to expand
title_frame.grid_columnconfigure(2, weight=1) # Allow column 2 to expand

# ahk scripts style
style = ttk.Style()
style.configure('My.TButton', font=('Calibri', 20), relief='flat')
style.configure('Red.TFrame', background="#352323")
style.configure('Red.TLabel', background="#352323")

# list of ahk scripts running
scripts_frame = ttk.Frame(master=window, height=100)

ahk_scripts_tk(ahk_scripts)

scripts_frame.pack(fill="x", expand=False, side="top")


# run window
window.mainloop()


