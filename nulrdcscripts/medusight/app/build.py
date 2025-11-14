"""
Cross-platform build script for MeduSight
Supports Windows (.exe + installer) and macOS (.app + .dmg)
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def get_platform():
    """Detect the current platform"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        raise Exception(f"Unsupported platform: {system}")

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous builds...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            import shutil
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")

def create_icons():
    """Create platform-specific icons from logo"""
    print("🎨 Creating platform-specific icons...")
    
    try:
        from PIL import Image
    except ImportError:
        print("   ⚠️  Pillow not installed, skipping icon creation")
        print("   Install with: poetry add pillow")
        return
    
    logo_path = Path("app/medusight_logo.png")
    if not logo_path.exists():
        print(f"   ⚠️  Logo not found at {logo_path}")
        return
    
    current_platform = get_platform()
    
    if current_platform == "windows":
        # Create .ico for Windows
        ico_path = Path("app/icon.ico")
        img = Image.open(logo_path)
        img.save(ico_path, format='ICO', sizes=[
            (256, 256), (128, 128), (64, 64), 
            (48, 48), (32, 32), (16, 16)
        ])
        print(f"   ✓ Created {ico_path}")
    
    elif current_platform == "macos":
        # Create .icns for macOS
        print("   Creating macOS icon set...")
        iconset_dir = Path("MeduSight.iconset")
        iconset_dir.mkdir(exist_ok=True)
        
        img = Image.open(logo_path)
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        
        for size in sizes:
            # Standard resolution
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(iconset_dir / f"icon_{size}x{size}.png")
            
            # Retina resolution (2x)
            if size <= 512:
                resized_2x = img.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
                resized_2x.save(iconset_dir / f"icon_{size}x{size}@2x.png")
        
        # Convert to .icns using iconutil
        subprocess.run(['iconutil', '-c', 'icns', str(iconset_dir)])
        
        # Move to app directory
        icns_path = Path("MeduSight.icns")
        if icns_path.exists():
            icns_path.rename("app/icon.icns")
            print(f"   ✓ Created app/icon.icns")
        
        # Clean up iconset directory
        import shutil
        shutil.rmtree(iconset_dir)

def build_pyinstaller():
    """Build executable with PyInstaller"""
    print("📦 Building with PyInstaller...")
    
    current_platform = get_platform()
    
    # Create spec file dynamically
    spec_content = create_spec_file(current_platform)
    spec_path = Path("medusight.spec")
    
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    print(f"   ✓ Created {spec_path}")
    
    # Run PyInstaller
    cmd = ['poetry', 'run', 'pyinstaller', 'medusight.spec', '--clean']
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("   ❌ PyInstaller build failed!")
        sys.exit(1)
    
    print("   ✓ PyInstaller build complete")

def create_spec_file(platform_name):
    """Generate platform-specific PyInstaller spec file"""
    
    if platform_name == "windows":
        icon_file = "'app/icon.ico'"
        console = "False"
    elif platform_name == "macos":
        icon_file = "'app/icon.icns'"
        console = "False"
    else:
        icon_file = "None"
        console = "False"
    
    spec = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/web', 'web'),
        ('medusight/mainprocessing/data', 'medusight/mainprocessing/data'),
        ('app/medusight_logo.png', '.'),
    ],
    hiddenimports=[
        'eel',
        'bottle',
        'bottle_websocket',
        'gevent',
        'geventwebsocket',
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MeduSight',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={icon_file},
)

"""
    
    if platform_name == "macos":
        spec += """
app = BUNDLE(
    exe,
    name='MeduSight.app',
    icon='app/icon.icns',
    bundle_identifier='edu.northwestern.medusight',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': '© 2025 Northwestern University',
    },
)
"""
    
    return spec

def create_windows_installer():
    """Create Windows installer using Inno Setup"""
    print("📀 Creating Windows installer...")
    
    # Check if Inno Setup is installed
    inno_path = Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe")
    if not inno_path.exists():
        print("   ⚠️  Inno Setup not found")
        print("   Download from: https://jrsoftware.org/isdl.php")
        print("   Skipping installer creation")
        return
    
    # Create Inno Setup script
    iss_content = """[Setup]
AppName=MeduSight
AppVersion=1.0.0
AppPublisher=Northwestern University
AppPublisherURL=https://github.com/northwestern/medusight
DefaultDirName={autopf}\\MeduSight
DefaultGroupName=MeduSight
OutputDir=installer
OutputBaseFilename=MeduSight-Setup-Windows
Compression=lzma
SolidCompression=yes
SetupIconFile=app\\icon.ico
UninstallDisplayIcon={app}\\MeduSight.exe
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\MeduSight.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\\MeduSight"; Filename: "{app}\\MeduSight.exe"
Name: "{group}\\Uninstall MeduSight"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\MeduSight"; Filename: "{app}\\MeduSight.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\MeduSight.exe"; Description: "{cm:LaunchProgram,MeduSight}"; Flags: nowait postinstall skipifsilent
"""
    
    with open("installer.iss", 'w') as f:
        f.write(iss_content)
    
    # Run Inno Setup
    subprocess.run([str(inno_path), "installer.iss"])
    print("   ✓ Windows installer created in installer/")

def create_macos_dmg():
    """Create macOS DMG installer"""
    print("📀 Creating macOS DMG...")
    
    try:
        import dmgbuild
    except ImportError:
        print("   ⚠️  dmgbuild not installed")
        print("   Install with: poetry add --group dev dmgbuild")
        print("   Skipping DMG creation")
        return
    
    # Create DMG settings
    settings_content = """
import os.path

application = 'dist/MeduSight.app'
appname = os.path.basename(application)

format = 'UDBZ'
size = '500M'
files = [application]
symlinks = {'Applications': '/Applications'}

icon_locations = {
    appname: (140, 120),
    'Applications': (500, 120)
}

background = 'builtin-arrow'
window_rect = ((100, 100), (640, 280))
icon_size = 128
text_size = 16
"""
    
    with open("dmg_settings.py", 'w') as f:
        f.write(settings_content)
    
    # Build DMG
    subprocess.run([
        'dmgbuild',
        '-s', 'dmg_settings.py',
        'MeduSight',
        'dist/MeduSight.dmg'
    ])
    
    print("   ✓ macOS DMG created at dist/MeduSight.dmg")

def main():
    """Main build process"""
    print("🚀 MeduSight Build Script")
    print("=" * 50)
    
    current_platform = get_platform()
    print(f"Platform: {current_platform}")
    print()
    
    # Step 1: Clean
    clean_build()
    print()
    
    # Step 2: Create icons
    create_icons()
    print()
    
    # Step 3: Build with PyInstaller
    build_pyinstaller()
    print()
    
    # Step 4: Create installer
    if current_platform == "windows":
        create_windows_installer()
    elif current_platform == "macos":
        create_macos_dmg()
    
    print()
    print("=" * 50)
    print("✅ Build complete!")
    print()
    
    if current_platform == "windows":
        print("📦 Executable: dist/MeduSight.exe")
        print("📦 Installer:  installer/MeduSight-Setup-Windows.exe")
    elif current_platform == "macos":
        print("📦 Application: dist/MeduSight.app")
        print("📦 DMG:         dist/MeduSight.dmg")
    
    print()

if __name__ == "__main__":
    main()