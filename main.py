import psutil
ahk_scripts = None

# get running scripts
def get_running_ahk_scripts():
    running_scripts = []
    for process in psutil.process_iter(['name','pid','cmdline']):
        try:
            if "autohotkey.exe" in process.info['name'].lower():
                cmdline = process.info['cmdline']
                if cmdline and len(cmdline) > 1:
                    # format everything into "running_scripts" array
                    script_path = cmdline[1]
                    name = script_path.split("\\")[-1].split(".")[0]
                    running_scripts.append({
                        'script_name': name,
                        'pid': process.info['pid'],
                        'path': script_path
                    })
        # throw out everything that isn't an AHK script
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return running_scripts

# run the "get_running_ahk_scripts()" function if this file is being used from another file
if __name__ == "main":
    ahk_scripts = get_running_ahk_scripts()