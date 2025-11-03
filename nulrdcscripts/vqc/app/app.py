import eel
import os
import sys
import glob
import platform
import traceback
from pathlib import Path

# === FIX: Add PARENT directory to Python path ===
# app.py is in app/ folder, medusight/ is in parent folder
# So we need to go UP one level from app.py's location
script_dir = Path(__file__).parent  # This is app/
parent_dir = script_dir.parent       # This is nulrdcscripts/

# Add parent to path so we can import medusight
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

print(f"Script directory: {script_dir}")
print(f"Parent directory (where medusight is): {parent_dir}")
print(f"Python will look for medusight in: {parent_dir}")

# Simplify web path (relative to app.py location)
web_path = os.path.join(script_dir, 'web')
eel.init(web_path)

# Create uploads directory (relative to app.py location)
uploads_dir = os.path.join(script_dir, 'uploads')
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

# Now import medusight - should work!
try:
    from medusight import processfile
    from medusight.mainprocessing import params
    print("✓ Successfully imported medusight.processfile")
except ImportError as e:
    print(f"✗ Failed to import medusight: {e}")
    print(f"   Check that medusight folder exists at: {parent_dir / 'medusight'}")
    sys.exit(1)

# ============================================================================
# PROCESSING FUNCTIONS WITH SETTINGS SUPPORT
# ============================================================================

def process_single_video(file_path, crop_mode='auto', manual_crop=None, 
                        sample_interval=900, analyze_audio=True,
                        audio_standard='broadcast', target_lufs=None, 
                        max_true_peak=None):
    """
    Process a single video file with settings.
    
    Args:
        file_path: Path to video file
        crop_mode: 'auto', 'combined', 'headswitching', 'off', 'manual'
        manual_crop: Manual crop string (if crop_mode='manual')
        sample_interval: Frame sampling interval for crop detection
        analyze_audio: Whether to run audio analysis
        audio_standard: 'broadcast', 'streaming', or 'film'
        target_lufs: Custom target LUFS (overrides standard)
        max_true_peak: Custom max true peak (overrides standard)
    """
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
                    # Extract issues from report
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
        print(f"Error processing {file_path}:")
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

# ============================================================================
# EEL EXPOSED FUNCTIONS
# ============================================================================

@eel.expose
def process_video(file_path):
    """Legacy function - redirects to process_single_video"""
    return process_single_video(file_path)

@eel.expose
def test_connection():
    print("Test connection called!")
    return {
        'status': 'connected',
        'message': 'MeduSight backend ready'
    }

@eel.expose
def get_file_info(file_path):
    """Get information about a video file"""
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

# ============================================================================
# CROSS-PLATFORM FILE DIALOGS
# ============================================================================

# Global variable to store current mode
current_file_mode = 'video'

@eel.expose
def set_file_mode(mode):
    """Set the current file selection mode"""
    global current_file_mode
    current_file_mode = mode
    print(f"Mode set to: {mode}")
    return True

@eel.expose
def select_files_dialog(file_types=None):
    """Open native file picker - cross-platform (macOS and Windows)"""
    try:
        # Use global mode if parameter is None
        global current_file_mode
        mode_to_use = file_types if file_types is not None else current_file_mode
        
        print(f"DEBUG: select_files_dialog called with file_types='{file_types}' (type: {type(file_types)})")
        print(f"DEBUG: Using mode: '{mode_to_use}'")
        
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            return _select_files_macos(mode_to_use)
        else:  # Windows or Linux
            return _select_files_windows(mode_to_use)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def _select_files_macos(file_types):
    """macOS file picker using AppleScript"""
    import subprocess
    
    # Handle both 'video' and 'xml' modes
    if file_types == 'xml':
        # Use proper UTI for XML and JSON
        file_type_list = '{"public.xml", "public.json"}'
        prompt_text = "Select QCTools XML/JSON files"
    else:  # video mode
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
    
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        files = [f.strip() for f in result.stdout.strip().split(',') if f.strip()]
        print(f"Selected files: {files}")
        return files
    else:
        print(f"Dialog cancelled or error: {result.stderr}")
        return []

def _select_files_windows(file_types):
    """Windows/Linux file picker using tkinter"""
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        # Handle both 'video' and 'xml' modes
        if file_types == 'xml':
            filetypes = [
                ("QCTools files", "*.xml *.json"),
                ("XML files", "*.xml"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
            title = "Select QCTools XML/JSON files"
        else:  # default to video
            filetypes = [
                ("Video files", "*.mkv *.mp4"),
                ("MKV files", "*.mkv"),
                ("MP4 files", "*.mp4"),
                ("All files", "*.*")
            ]
            title = "Select Video Files"
        
        files = filedialog.askopenfilenames(
            title=title,
            filetypes=filetypes
        )
        
        root.destroy()
        
        files_list = list(files) if files else []
        print(f"Selected files: {files_list}")
        return files_list
        
    except Exception as e:
        print(f"Error in Windows file dialog: {e}")
        import traceback
        traceback.print_exc()
        return []

@eel.expose  
def select_folder_dialog():
    """Open native folder picker and return the folder path - cross-platform"""
    try:
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            folder = _select_folder_macos()
        else:  # Windows or Linux
            folder = _select_folder_windows()
        
        if not folder:
            print("No folder selected")
            return None
        
        print(f"Selected folder: {folder}")
        return folder
        
    except Exception as e:
        print(f"Error opening folder dialog: {e}")
        import traceback
        traceback.print_exc()
        return None

def _select_folder_macos():
    """macOS folder picker using AppleScript"""
    import subprocess
    
    script = '''
    tell application "System Events"
        activate
        set theFolder to choose folder with prompt "Select folder containing files"
        return POSIX path of theFolder
    end tell
    '''
    
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        folder = result.stdout.strip()
        return folder if folder else None
    else:
        return None

def _select_folder_windows():
    """Windows/Linux folder picker using tkinter"""
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        folder = filedialog.askdirectory(
            title="Select folder containing files"
        )
        
        root.destroy()
        return folder if folder else None
        
    except Exception as e:
        print(f"Error in Windows folder dialog: {e}")
        return None

# ============================================================================
# FOLDER CONTENTS AND FILE PROCESSING
# ============================================================================

@eel.expose
def get_folder_contents(folder_path):
    """Get list of files in a folder based on current mode"""
    try:
        global current_file_mode
        from pathlib import Path
        path = Path(folder_path)
        
        print(f"DEBUG: get_folder_contents called with: {folder_path}")
        print(f"DEBUG: Current mode: {current_file_mode}")
        
        if not path.exists() or not path.is_dir():
            print(f"DEBUG: Path doesn't exist or is not a directory")
            return {
                'success': False,
                'message': 'Invalid folder path',
                'files': []
            }
        
        # Determine which extensions to look for based on mode
        if current_file_mode == 'xml':
            valid_extensions = ['.xml', '.json']
            print(f"DEBUG: Looking for XML/JSON files")
        else:  # video mode
            valid_extensions = ['.mkv', '.mp4']
            print(f"DEBUG: Looking for video files (MKV/MP4)")
        
        files_found = []
        for f in path.iterdir():
            if f.is_file():
                ext = f.suffix.lower()
                print(f"DEBUG: Checking file: {f.name}, extension: {ext}")
                
                # Check if file matches current mode
                if ext in valid_extensions:
                    files_found.append({
                        'filename': f.name,
                        'path': str(f),
                        'size': f.stat().st_size,
                        'extension': ext
                    })
                    print(f"DEBUG: ✓ Added: {f.name}")
                else:
                    print(f"DEBUG: ✗ Skipped: {f.name} (extension '{ext}' not in {valid_extensions})")
        
        print(f"DEBUG: Total files found: {len(files_found)}")
        
        return {
            'success': len(files_found) > 0,
            'files': files_found,
            'count': len(files_found)
        }
    
    except Exception as e:
        print(f"ERROR in get_folder_contents: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': str(e),
            'files': []
        }

@eel.expose
def process_single_file(file_path, crop_mode='auto', manual_crop=None, 
                       sample_interval=900, analyze_audio=True,
                       audio_standard='broadcast', target_lufs=None, 
                       max_true_peak=None):
    """
    Process a single file with settings - exposed to JavaScript.
    Matches the signature expected by main.js
    """
    return process_single_video(
        file_path, crop_mode, manual_crop, sample_interval,
        analyze_audio, audio_standard, target_lufs, max_true_peak
    )

@eel.expose
def process_manual_path(path_input, crop_mode='auto', manual_crop=None,
                       sample_interval=900, analyze_audio=True,
                       audio_standard='broadcast', target_lufs=None,
                       max_true_peak=None):
    """
    BACKUP ONLY: Process single file or folder from manual path input.
    This is a fallback for when file dialogs fail.
    """
    try:
        global current_file_mode
        from pathlib import Path
        path = Path(path_input)
        
        print(f"DEBUG: process_manual_path called with: {path_input}")
        print(f"DEBUG: Current mode: {current_file_mode}")
        
        if not path.exists():
            return {'success': False, 'error': 'Path does not exist'}
        
        # Determine valid extensions based on mode
        if current_file_mode == 'xml':
            valid_extensions = ['.xml', '.json']
        else:
            valid_extensions = ['.mkv', '.mp4']
        
        if path.is_file():
            # Check if it's a supported file type for current mode
            ext = path.suffix.lower()
            if ext in valid_extensions:
                # Process the file and return results
                result = process_single_video(
                    path, crop_mode, manual_crop, sample_interval,
                    analyze_audio, audio_standard, target_lufs, max_true_peak
                )
                return {
                    'success': True,
                    'is_folder': False,
                    'result': result
                }
            else:
                return {
                    'success': False, 
                    'error': f'File type {ext} not supported in {current_file_mode} mode'
                }
        
        elif path.is_dir():
            # Get all supported files in folder (don't process yet, let JS handle that)
            files_found = []
            for f in path.iterdir():
                if f.is_file() and f.suffix.lower() in valid_extensions:
                    files_found.append({
                        'filename': f.name,
                        'path': str(f),
                        'size': f.stat().st_size
                    })
            
            if files_found:
                return {
                    'success': True,
                    'is_folder': True,
                    'files': files_found
                }
            else:
                return {
                    'success': False,
                    'error': f'No {current_file_mode} files found in folder'
                }
        
        return {'success': False, 'error': 'Invalid path'}
    
    except Exception as e:
        print(f"ERROR in process_manual_path: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

@eel.expose
def process_path(path_input):
    """Legacy function - redirects to process_manual_path"""
    return process_manual_path(path_input)

@eel.expose
def open_report_file(report_path):
    """Open the report file in the default text editor - cross-platform"""
    try:
        import platform
        import subprocess
        
        system = platform.system()
        
        print(f"DEBUG: Opening report file: {report_path}")
        
        if system == 'Darwin':  # macOS
            subprocess.run(['open', report_path])
        elif system == 'Windows':
            os.startfile(report_path)  # More reliable for Windows
        else:  # Linux
            subprocess.run(['xdg-open', report_path])
        
        return {'success': True}
    except Exception as e:
        print(f"ERROR opening report file: {e}")
        return {'success': False, 'error': str(e)}

@eel.expose
def read_report_file(report_path):
    """Read report file content and return it"""
    try:
        from pathlib import Path
        path = Path(report_path)
        
        print(f"DEBUG: read_report_file called with: {report_path}")
        
        if not path.exists():
            print(f"DEBUG: File does not exist: {report_path}")
            return {'success': False, 'error': 'Report file not found'}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"DEBUG: Successfully read {len(content)} characters")
        return {
            'success': True,
            'content': content
        }
    except Exception as e:
        print(f"ERROR in read_report_file: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

# Start the app
if __name__ == '__main__':
    eel.start('index.html', 
              size=(1200, 900),
              mode='chrome',
              port=8080)