import eel
import os
import sys
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
        
        return {'filename': filename,
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
        
        # Your video quality control logic here
        # Example processing:
        # - Check video codec
        # - Verify audio tracks
        # - Check resolution
        # - Validate duration
        # etc.
        
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

@eel.expose
def browse_file():
    """Open file dialog (alternative approach)"""
    # Note: File dialogs work better through HTML input type="file"
    # But you can also use tkinter if needed
    pass

@eel.expose
def select_files_dialog():
    """Open native file picker using AppleScript (macOS specific)"""
    try:
        import subprocess
        
        # Use macOS native AppleScript file dialog
        script = '''
        tell application "System Events"
            activate
            set theFiles to choose file with prompt "Select QCTools XML/JSON files" of type {"xml", "json"} with multiple selections allowed
            set filePaths to {}
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
            # Parse the comma-separated file paths
            files = [f.strip() for f in result.stdout.strip().split(',') if f.strip()]
            print(f"Selected files: {files}")
            return files
        else:
            print(f"Dialog cancelled or error: {result.stderr}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

@eel.expose  
def select_folder_dialog():
    """Open native folder picker using PyQt5"""
    try:
        from PyQt5.QtWidgets import QApplication, QFileDialog
        import sys
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        folder = QFileDialog.getExistingDirectory(
            None,
            "Select folder containing QCTools files",
            ""
        )
        
        print(f"Selected folder: {folder}")
        return folder if folder else None
    except Exception as e:
        print(f"Error opening folder dialog: {e}")
        import traceback
        traceback.print_exc()
        return None


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
            if f.suffix.lower() in ['.xml', '.json'] or str(f).lower().endswith('.mkv.qctools.xml'):
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
            if path.suffix.lower() in ['.xml', '.json'] or str(path).lower().endswith('.mkv.qctools.xml'):
                result = process_single_video(path)
                results.append(result)
            else:
                return {'success': False, 'message': f'Unsupported file type: {path.suffix}', 'results': []}
        
        elif path.is_dir():
            # Process all XML/JSON files in folder
            for f in path.glob('*'):
                if f.suffix.lower() in ['.xml', '.json'] or str(f).lower().endswith('.mkv.qctools.xml'):
                    result = process_single_video(f)
                    results.append(result)
            
            if not results:
                return {'success': False, 'message': 'No QCTools files found in folder', 'results': []}
        
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
    """Open the report file in the default text editor"""
    try:
        import platform
        import subprocess
        
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            subprocess.run(['open', report_path])
        elif system == 'Windows':
            subprocess.run(['start', report_path], shell=True)
        else:  # Linux
            subprocess.run(['xdg-open', report_path])
        
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Start the app\
eel.start('index.html', 
          size=(1200, 900),
          mode='chrome',
          port=8080)