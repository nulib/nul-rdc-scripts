import os
import platform

def build():
    system = platform.system()
    separator = ';' if system == 'Windows' else ':'
    
    # Determine icon file
    if system == 'Windows':
        icon = 'icon.ico'
    elif system == 'Darwin':  # Mac
        icon = 'icon.icns'
    else:  # Linux
        icon = 'icon.png'
    
    # Check if icon exists
    if not os.path.exists(icon):
        print(f"Warning: {icon} not found. Building without icon.")
        icon_flag = ''
    else:
        icon_flag = f' --icon="{icon}"'
    
    cmd = (f'pyinstaller --onefile --windowed '
           f'--add-data "web{separator}web" '
           f'--name "MKV_Processor"'
           f'{icon_flag} app.py')
    
    print(f"Building for {system}...")
    os.system(cmd)
    print("Build complete!")

if __name__ == '__main__':
    build()