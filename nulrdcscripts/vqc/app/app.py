import eel
import os
import sys
import glob
import platform
from pathlib import Path

# Add parent directory to path so we can import medusight
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Handle PyInstaller paths
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

web_path = os.path.join(base_path, 'web')
eel.init(web_path)

# Create uploads directory
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

def process_single_video(file_path):
    """Process a single video file - calls medusight processfile"""
    try:
        from pathlib import Path
        path = Path(file_path)
        print(f"Processing: {path.name}")
        
        # Mock command-line arguments for medusight
        import sys
        old_argv = sys.argv
        sys.argv = ['app.py', '--input', str(path), '--output', 'input']
        
        try:
            # Get file extension first
            extension = path.suffix.lower() if path.suffix else '.unknown'
            file_size = path.stat().st_size if path.exists() else 0
            
            # Call your medusight processfile function
            from medusight.medusight import processfile
            
            # Process the file (output goes to same directory as input)
            processfile(str(path), 'input')
        finally:
            # Restore original argv
            sys.argv = old_argv
        
        # After processing, check for output files
        base_filename = path.stem.replace('.mkv.qctools', '').replace('.xml', '').replace('.json', '')
        output_dir = path.parent
        video_report = output_dir / f"{base_filename}_video_level_report.txt"
        
        # Read the report to get PASS/FAIL status
        if video_report.exists():
            with open(video_report, 'r') as f:
                report_content = f.read()
            
            status = 'PASS' if 'PASS' in report_content else 'FAIL'
            
            issues = []
            if status == 'FAIL':
                issues.append('Quality control issues detected - check report file')
            
            return {
                'filename': path.name,
                'path': str(path),
                'size': file_size,
                'extension': extension,
                'status': status,
                'issues': issues,
                'processed': True,
                'report_path': str(video_report)
            }
        else:
            return {
                'filename': path.name,
                'path': str(path),
                'size': file_size,
                'extension': extension,
                'status': 'ERROR',
                'issues': ['Report file not generated'],
                'processed': False
            }
            
    except Exception as e:
        import traceback
        print(f"Error processing {file_path}:")
        print(traceback.format_exc())
        
        # Make sure we always return all required fields
        try:
            from pathlib import Path
            path = Path(file_path)
            filename = path.name
            size = path.stat().st_size if path.exists() else 0
            extension = path.suffix.lower() if path.suffix else '.unknown'
        except:
            filename = str(file_path)
            size = 0
            extension = '.unknown'
        
        return {
            'filename': filename,
            'path': str(file_path),
            'size': size,
            'extension': extension,
            'status': 'ERROR',
            'issues': [str(e)],
            'processed': False
        }

@eel.expose
def process_video(file_path):
    """Process video file - your QC logic here"""
    try:
        print(f"Processing: {file_path}")
        
        return {
            'success': True,
            'message': f"Successfully processed: {os.path.basename(file_path)}",
            'details': {
                'filename': os.path.basename(file_path),
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

@eel.expose
def test_connection():
    print("Test connection called!")
    return "Connection works!"

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
def select_folder_dialog(file_types=None):
    """Open native folder picker and return all matching files - cross-platform"""
    try:
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            folder = _select_folder_macos()
        else:  # Windows or Linux
            folder = _select_folder_windows()
        
        if not folder:
            print("No folder selected")
            return []
        
        print(f"Selected folder: {folder}")
        
        # Determine which file types to look for
        if file_types is None or file_types == 'video':
            extensions = ['*.mkv', '*.mp4', '*.MKV', '*.MP4']
        else:
            extensions = ['*.xml', '*.json', '*.XML', '*.JSON']
        
        # Find all matching files in the folder (non-recursive)
        all_files = []
        for ext in extensions:
            pattern = os.path.join(folder, ext)
            all_files.extend(glob.glob(pattern))
        
        # Remove duplicates (case-insensitive extensions might cause this)
        all_files = list(set(all_files))
        
        print(f"Found {len(all_files)} files in folder")
        return all_files
        
    except Exception as e:
        print(f"Error opening folder dialog: {e}")
        import traceback
        traceback.print_exc()
        return []

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
    """Get list of QCTools files in a folder"""
    try:
        from pathlib import Path
        path = Path(folder_path)
        
        if not path.exists() or not path.is_dir():
            return {
                'success': False,
                'message': 'Invalid folder path',
                'files': []
            }
        
        qc_files = []
        for f in path.glob('*'):
            if f.suffix.lower() in ['.xml', '.json', '.mkv', '.mp4'] or str(f).lower().endswith('.mkv.qctools.xml'):
                qc_files.append({
                    'filename': f.name,
                    'path': str(f),
                    'size': f.stat().st_size,
                    'extension': f.suffix.lower()
                })
        
        return {
            'success': True,
            'files': qc_files,
            'count': len(qc_files)
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'files': []
        }
        
@eel.expose
def process_single_file(file_path):
    """Process a single file - exposed to JavaScript"""
    return process_single_video(file_path)

@eel.expose
def process_path(path_input):
    """Process single file or folder from path string"""
    try:
        from pathlib import Path
        path = Path(path_input)
        
        if not path.exists():
            return {'success': False, 'message': 'Path does not exist', 'results': []}
        
        results = []
        
        if path.is_file():
            # Check if it's a supported file type
            if path.suffix.lower() in ['.xml', '.json', '.mkv', '.mp4'] or str(path).lower().endswith('.mkv.qctools.xml'):
                result = process_single_video(path)
                results.append(result)
            else:
                return {'success': False, 'message': f'Unsupported file type: {path.suffix}', 'results': []}
        
        elif path.is_dir():
            # Process all supported files in folder
            for f in path.glob('*'):
                if f.suffix.lower() in ['.xml', '.json', '.mkv', '.mp4'] or str(f).lower().endswith('.mkv.qctools.xml'):
                    result = process_single_video(f)
                    results.append(result)
            
            if not results:
                return {'success': False, 'message': 'No supported files found in folder', 'results': []}
        
        return {
            'success': True, 
            'message': f'Processed {len(results)} file(s)', 
            'results': results
        }
    
    except Exception as e:
        import traceback
        print(f"Error in process_path:")
        print(traceback.format_exc())
        return {
            'success': False, 
            'message': str(e), 
            'results': []
        }

@eel.expose
def open_report_file(report_path):
    """Open the report file in the default text editor - cross-platform"""
    try:
        import platform
        import subprocess
        
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            subprocess.run(['open', report_path])
        elif system == 'Windows':
            os.startfile(report_path)  # More reliable for Windows
        else:  # Linux
            subprocess.run(['xdg-open', report_path])
        
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Start the app
if __name__ == '__main__':
    eel.start('index.html', 
              size=(1200, 900),
              mode='chrome',
              port=8080)