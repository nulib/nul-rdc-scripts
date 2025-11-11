import eel
import os
import sys
import platform
import traceback
import socket
import time
import subprocess
import webbrowser
from pathlib import Path

# === HIDE CONSOLE WINDOW ON WINDOWS ===
if platform.system() == 'Windows':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# === FIX: Add PARENT directory to Python path ===
def get_base_path():
    """Get the base path, accounting for PyInstaller bundling."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent

def find_free_port():
    """Find an available port for the Eel server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def write_port_file(port):
    """Write the port number to a file for Electron to read."""
    if getattr(sys, 'frozen', False):
        port_file = Path(sys.executable).parent / 'port.txt'
    else:
        port_file = Path(__file__).parent.parent / 'port.txt'
    
    with open(port_file, 'w') as f:
        f.write(str(port))

# Setup paths
base_path = get_base_path()
script_dir = Path(__file__).parent if not getattr(sys, 'frozen', False) else base_path / 'app'
parent_dir = base_path

# Add parent to path so we can import medusight
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Simplify web path
if getattr(sys, 'frozen', False):
    web_path = os.path.join(sys._MEIPASS, 'web')
else:
    web_path = os.path.join(script_dir, 'web')

# Create uploads directory
if getattr(sys, 'frozen', False):
    uploads_dir = Path(sys.executable).parent / 'uploads'
else:
    uploads_dir = script_dir / 'uploads'

if not uploads_dir.exists():
    uploads_dir.mkdir(parents=True)

# Initialize Eel
eel.init(web_path)

# Now import medusight - should work!
try:
    from medusight import processfile
    from medusight.mainprocessing import params
except ImportError as e:
    sys.exit(1)

# [Keep all your existing functions - process_single_video, @eel.expose functions, etc.]
# ... [ALL THE MIDDLE CODE STAYS EXACTLY THE SAME] ...

# ============================================================================
# PROCESSING FUNCTIONS WITH SETTINGS SUPPORT
# ============================================================================

def process_single_video(file_path, crop_mode='auto', manual_crop=None,
                        sample_interval=900, analyze_audio=True,
                        audio_standard='broadcast', target_lufs=None,
                        max_true_peak=None):
    """Process a single video file with settings."""
    start_time = time.time()
    
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
    else:
        return {
            'success': False,
            'filename': os.path.basename(file_path),
            'status': 'ERROR',
            'issues': ['File not found'],
            'error': 'File not found'
        }
    
    try:
        # Update params with settings
        params.args.crop_mode = crop_mode
        params.args.manual_crop = manual_crop
        params.args.sample_interval = sample_interval
        params.args.analyze_audio = analyze_audio
        params.args.audio_standard = audio_standard
        params.args.target_lufs = target_lufs
        params.args.max_true_peak = max_true_peak

        # Process the file
        process_start = time.time()
        result = processfile(str(file_path), 'input')

        # Build response with report paths
        path = Path(file_path)
        base_name = path.stem.replace('.mkv.qctools', '').replace('.xml', '').replace('.json', '')
        output_dir = path.parent

        video_report = output_dir / f"{base_name}_video_level_report.txt"
        frames_report = output_dir / f"{base_name}_failing_frames_by_criteria.txt"
        audio_report = output_dir / f"{base_name}_audio_report.txt"

        # Determine pass/fail status
        status = 'PASS'
        issues = []

        if video_report.exists():
            with open(video_report, 'r') as f:
                content = f.read()
                if 'FAIL' in content or 'out_of_range' in content or 'clipping' in content:
                    status = 'FAIL'
                    for line in content.split('\n'):
                        if 'Criteria:' in line and ('FAIL' in line or 'out_of_range' in line):
                            issues.append(line.strip())

        return {
            'success': True,
            'filename': path.name,
            'path': str(path),
            'status': status,
            'issues': issues,
            'size': path.stat().st_size,
            'extension': path.suffix.lower(),
            'processed': True,
            'report_path': str(video_report) if video_report.exists() else None,
            'frames_report_path': str(frames_report) if frames_report.exists() else None,
            'audio_report_path': str(audio_report) if (analyze_audio and audio_report.exists()) else None
        }

    except Exception as e:
        traceback.print_exc()
        return {
            'success': False,
            'filename': os.path.basename(file_path),
            'path': str(file_path),
            'status': 'ERROR',
            'issues': [str(e)],
            'size': 0,
            'extension': os.path.splitext(file_path)[1].lower(),
            'processed': False,
            'report_path': None,
            'frames_report_path': None,
            'audio_report_path': None,
            'error': str(e)
        }

# [ALL YOUR @eel.expose FUNCTIONS - KEEP THEM EXACTLY AS THEY ARE]

@eel.expose
def process_video(file_path):
    return process_single_video(file_path)

@eel.expose
def test_connection():
    return {'status': 'connected', 'message': 'MeduSight backend ready'}

@eel.expose
def get_file_info(file_path):
    try:
        if not os.path.exists(file_path):
            return {'error': 'File not found'}
        return {
            'filename': os.path.basename(file_path),
            'size': os.path.getsize(file_path),
            'path': file_path,
            'exists': True
        }
    except Exception as e:
        return {'error': str(e)}

current_file_mode = 'video'

@eel.expose
def set_file_mode(mode):
    global current_file_mode
    current_file_mode = mode
    return True

@eel.expose
def select_files_dialog(file_types=None):
    try:
        global current_file_mode
        mode_to_use = file_types if file_types is not None else current_file_mode
        system = platform.system()
        if system == 'Darwin':
            return _select_files_macos(mode_to_use)
        else:
            return _select_files_windows(mode_to_use)
    except Exception as e:
        traceback.print_exc()
        return []

def _select_files_macos(file_types):
    import subprocess
    if file_types == 'xml':
        file_type_list = '{"public.xml", "public.json"}'
        prompt_text = "Select QCTools XML/JSON files"
    else:
        file_type_list = '{"public.mpeg-4", "org.matroska.mkv"}'
        prompt_text = "Select Video Files (MKV/MP4)"

    script = f'''
    tell application "System Events"
        activate
        set theFiles to choose file with prompt "{prompt_text}" of type {file_type_list} with multiple selections allowed
        set filePaths to {{}}
        repeat with aFile in theFiles
            set end of filePaths to POSIX path of aFile
        end repeat
        return filePaths
    end tell
    '''

    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.returncode == 0:
        return [f.strip() for f in result.stdout.strip().split(',') if f.strip()]
    return []

def _select_files_windows(file_types):
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        if file_types == 'xml':
            filetypes = [
                ("QCTools files", "*.xml *.json"),
                ("XML files", "*.xml"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
            title = "Select QCTools XML/JSON files"
        else:
            filetypes = [
                ("Video files", "*.mkv *.mp4"),
                ("MKV files", "*.mkv"),
                ("MP4 files", "*.mp4"),
                ("All files", "*.*")
            ]
            title = "Select Video Files"

        files = filedialog.askopenfilenames(title=title, filetypes=filetypes)
        root.destroy()
        return list(files) if files else []
    except Exception as e:
        traceback.print_exc()
        return []

@eel.expose
def select_folder_dialog():
    try:
        system = platform.system()
        folder = _select_folder_macos() if system == 'Darwin' else _select_folder_windows()
        return folder
    except Exception as e:
        traceback.print_exc()
        return None

def _select_folder_macos():
    import subprocess
    script = '''
    tell application "System Events"
        activate
        set theFolder to choose folder with prompt "Select folder containing files"
        return POSIX path of theFolder
    end tell
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None

def _select_folder_windows():
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder = filedialog.askdirectory(title="Select folder containing files")
        root.destroy()
        return folder if folder else None
    except Exception as e:
        return None

@eel.expose
def get_folder_contents(folder_path):
    try:
        global current_file_mode
        from pathlib import Path
        path = Path(folder_path)

        if not path.exists() or not path.is_dir():
            return {'success': False, 'message': 'Invalid folder path', 'files': []}

        valid_extensions = ['.xml', '.json'] if current_file_mode == 'xml' else ['.mkv', '.mp4']

        files_found = []
        for f in path.iterdir():
            if f.is_file() and f.suffix.lower() in valid_extensions:
                files_found.append({
                    'filename': f.name,
                    'path': str(f),
                    'size': f.stat().st_size,
                    'extension': f.suffix.lower()
                })

        return {'success': len(files_found) > 0, 'files': files_found, 'count': len(files_found)}
    except Exception as e:
        traceback.print_exc()
        return {'success': False, 'message': str(e), 'files': []}

@eel.expose
def process_single_file(file_path, crop_mode='auto', manual_crop=None,
                       sample_interval=900, analyze_audio=True,
                       audio_standard='broadcast', target_lufs=None,
                       max_true_peak=None):
    return process_single_video(
        file_path, crop_mode, manual_crop, sample_interval,
        analyze_audio, audio_standard, target_lufs, max_true_peak
    )

@eel.expose
def process_manual_path(path_input, crop_mode='auto', manual_crop=None,
                       sample_interval=900, analyze_audio=True,
                       audio_standard='broadcast', target_lufs=None,
                       max_true_peak=None):
    try:
        global current_file_mode
        from pathlib import Path
        path = Path(path_input)

        if not path.exists():
            return {'success': False, 'error': 'Path does not exist'}

        valid_extensions = ['.xml', '.json'] if current_file_mode == 'xml' else ['.mkv', '.mp4']

        if path.is_file():
            ext = path.suffix.lower()
            if ext in valid_extensions:
                result = process_single_video(
                    path, crop_mode, manual_crop, sample_interval,
                    analyze_audio, audio_standard, target_lufs, max_true_peak
                )
                return {'success': True, 'is_folder': False, 'result': result}
            else:
                return {'success': False, 'error': f'File type {ext} not supported in {current_file_mode} mode'}

        elif path.is_dir():
            files_found = []
            for f in path.iterdir():
                if f.is_file() and f.suffix.lower() in valid_extensions:
                    files_found.append({
                        'filename': f.name,
                        'path': str(f),
                        'size': f.stat().st_size
                    })

            if files_found:
                return {'success': True, 'is_folder': True, 'files': files_found}
            else:
                return {'success': False, 'error': f'No {current_file_mode} files found in folder'}

        return {'success': False, 'error': 'Invalid path'}

    except Exception as e:
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

@eel.expose
def process_path(path_input):
    return process_manual_path(path_input)

@eel.expose
def open_report_file(report_path):
    try:
        import subprocess
        system = platform.system()
        if system == 'Darwin':
            subprocess.run(['open', report_path])
        elif system == 'Windows':
            os.startfile(report_path)
        else:
            subprocess.run(['xdg-open', report_path])
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@eel.expose
def read_report_file(report_path):
    try:
        from pathlib import Path
        path = Path(report_path)

        if not path.exists():
            return {'success': False, 'error': 'Report file not found'}

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {'success': True, 'content': content}
    except Exception as e:
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

# ============================================================================
# BROWSER APP MODE LAUNCHER
# ============================================================================

def launch_browser_app_mode(url):
    """Launch browser in app mode."""
    system = platform.system()
    
    try:
        if system == 'Windows':
            chrome_paths = [
                'C:/Program Files/Google/Chrome/Application/chrome.exe',
                'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
                os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/Application/chrome.exe')
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    subprocess.Popen([chrome_path, f'--app={url}', '--window-size=1400,900'], 
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                    return
            
            subprocess.Popen(['msedge', f'--app={url}', '--window-size=1400,900'],
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif system == 'Darwin':
            chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, f'--app={url}', '--window-size=1400,900'])
            else:
                webbrowser.open(url)
        else:
            subprocess.Popen(['google-chrome', f'--app={url}', '--window-size=1400,900'])
            
    except Exception as e:
        webbrowser.open(url)

# ============================================================================
# START APPLICATION
# ============================================================================

def start_app():
    """Start the Eel application in browser app mode."""
    port = find_free_port()
    write_port_file(port)
    
    url = f'http://localhost:{port}'
    
    import threading
    threading.Timer(1.0, lambda: launch_browser_app_mode(url)).start()
    
    try:
        eel.start('index.html',
                  mode=None,
                  port=port,
                  host='localhost',
                  block=True)
    except:
        time.sleep(5)

if __name__ == '__main__':
    start_app()