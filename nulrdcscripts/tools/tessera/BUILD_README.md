# Tessera - Desktop Application Build Guide

## Prerequisites

1. **Install Node.js** (v18 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version` and `npm --version`

## Project Structure

Your project folder should contain:
```
tessera/
├── main.js           (Electron main process)
├── package.json      (Project configuration)
├── index.html        (Your HTML file)
├── styles.css        (Your CSS file)
├── app.js            (Your JavaScript file)
├── icon.png          (512x512px icon - optional)
├── icon.icns         (Mac icon - optional)
└── icon.ico          (Windows icon - optional)
```

## Setup Instructions

### 1. Initialize the Project

Open terminal/command prompt in your project folder:

```bash
# Install dependencies
npm install
```

This will install Electron and electron-builder.

### 2. Test the Application

Run the app in development mode:

```bash
npm start
```

The application should open in a desktop window.

### 3. Build for Distribution

**Build for current OS:**
```bash
npm run build
```

**Build for Mac only:**
```bash
npm run build:mac
```

**Build for Windows only:**
```bash
npm run build:win
```

**Build for both Mac and Windows:**
```bash
npm run build:all
```

### 4. Find Your Built Application

After building, find your application in the `dist/` folder:

**Mac:**
- `dist/tessera.dmg` (installer)
- `dist/mac/tessera.app` (application)

**Windows:**
- `dist/tessera.exe` (installer)
- `dist/tessera.exe` (portable version)

## Creating Application Icons (Optional)

For the best appearance, create custom icons:

### Mac Icon (.icns)
1. Create a 1024x1024 PNG image
2. Use an online converter (e.g., https://cloudconvert.com/png-to-icns)
3. Save as `icon.icns` in your project root

### Windows Icon (.ico)
1. Create a 256x256 PNG image
2. Use an online converter (e.g., https://convertico.com/)
3. Save as `icon.ico` in your project root

### Linux Icon (.png)
- Save a 512x512 PNG as `icon.png` in your project root

## Cross-Platform Building

### Building Windows App on Mac:
```bash
npm install --save-dev electron-builder
npm run build:win
```

### Building Mac App on Windows:
Mac apps (.dmg) can only be built on macOS due to code signing requirements.

## Distribution

### Mac Distribution:
- Share the `.dmg` file
- Users drag the app to their Applications folder
- Note: First-time users may need to right-click > Open to bypass Gatekeeper

### Windows Distribution:
- Share the `.exe` installer or portable `.exe`
- Users may see a Windows SmartScreen warning (click "More info" > "Run anyway")


## Troubleshooting

### "Module not found" errors
```bash
npm install
```

### Build fails on Mac
Make sure Xcode Command Line Tools are installed:
```bash
xcode-select --install
```

### Build fails on Windows
Install Windows Build Tools:
```bash
npm install --global windows-build-tools
```

### App won't open on Mac
Right-click the app > Open (first time only)

### Large file size
The app will be 100-200 MB because it includes Chromium and Node.js. This is normal for Electron apps.

## Features of Desktop Version

✅ Native menu bar with keyboard shortcuts /n
✅ Standalone application (no browser needed) /n
✅ File system access for saving/loading /n
✅ Works offline /n
✅ Professional appearance /n
✅ Cross-platform compatibility /n
✅ Smart memory management with notifications /n

## Working with Large WAV Files

### File Size Guidance

**Preservation-quality WAV files are large!** Here's what to expect:

| Duration | Approximate Size |
|----------|-----------------|
| 10 minutes | ~100 MB |
| 30 minutes | ~300 MB |
| 1 hour | ~600 MB |
| 2 hours | ~1.2 GB |
| 4 hours | ~2.4 GB |

### Memory Management

The application is designed to handle large WAV files efficiently with **automatic session protection and smart restart prompts**:

**✅ Automatic Session Save with Smart Warnings:**
When the app detects potential memory issues (after 3+ hours or 3GB+ of audio loaded):
1. **Automatically saves your session** as `[audiofilename]_session.json`
2. Shows a warning dialog with two options:
   - **Click OK**: Application closes immediately (recommended)
   - **Click Cancel**: Continue working normally
3. **If you ignore the warnings**: Automatic close after 2 minutes with additional reminders

**How the Timer Works:**
- **Initial warning appears** - You can close now (OK) or continue working (Cancel)
- **If you click Cancel** - You can continue working indefinitely 
- **If you ignore/don't respond** to the initial or follow-up warnings:
  - 1:00 remaining - Second warning appears
  - 0:30 remaining - Final warning appears
  - 0:00 - Application automatically closes

**Why This System?**
- ✅ Protects your work (automatically saved before any warnings)
- ✅ Gives you control (click Cancel to keep working)
- ✅ Prevents memory issues if warnings are ignored
- ✅ Multiple chances to respond before forced close

**✅ Manual Save Anytime:**
- Press **Ctrl/Cmd+S** to save manually
- Session saved as `[audiofilename]_session.json`
- WebVTT export saved as `[audiofilename].vtt`

**✅ Recommended Workflow:**
1. Work on your audio file and create captions
2. When memory warning appears:
   - **Option A**: Click OK to restart now (cleanest)
   - **Option B**: Click Cancel and finish your current thought, then manually close
3. Reopen and load your saved session (Ctrl/Cmd+L)
4. Continue working with fresh memory

**File Naming Convention:**
- Session files: `recording_name_session.json`
- WebVTT exports: `recording_name.vtt`
- Automatically uses your audio filename - no typing needed!

**Decision Tree:**
```
Memory threshold → Auto-save → Warning Dialog
↓
User Response:
├─ Click OK → Close immediately ✅ (Recommended)
├─ Click Cancel → Continue working normally ✅ (You're in control)
└─ No response/Ignore → Timer starts (2 minutes to auto-close)
    ├─ 1:00 warning (respond to continue)
    ├─ 0:30 warning (respond to continue)
    └─ 0:00 Auto-close 🔒
```

**Why This Helps:**
- Clears accumulated memory usage
- Prevents slowdowns during long sessions
- Ensures smooth performance throughout your work

### Best Practices for Large Files

**For files under 2 hours (~1.2GB):**
- Load and work directly without concern
- Single session should work smoothly

**For files 2-4 hours (~1.2-2.4GB):**
- Work in the application
- Save periodically (every 30-60 minutes)
- Consider one app restart midway through long sessions

**For files over 4 hours (>2.4GB):**
- You'll receive a warning when loading
- Strongly recommended: break into segments at natural points
  - Between lectures/presentations
  - Between musical movements
  - At intermissions or breaks
- Create separate VTT files, then combine if needed

**System Requirements for Large WAV Files:**
- **Minimum:** 8GB RAM
- **Recommended:** 16GB RAM for multiple large files
- **Storage:** SSD recommended for faster loading

### Troubleshooting Large Files

**If the application becomes slow:**
1. Save your session immediately
2. Close the application completely
3. Reopen and load your session
4. Performance should be restored

**If a file won't load:**
- File may be corrupted
- File may exceed your system's available memory
- Try closing other applications to free RAM
- Consider splitting the file into smaller segments

**Memory Tip:**
Session files (.json) are tiny (typically <1MB even with 1000+ captions), so save often! The audio file itself is NOT saved in the session, only your captions and metadata.

## Keyboard Shortcuts (Desktop)

- **Cmd/Ctrl+O** - Open audio file
- **Cmd/Ctrl+S** - Save session
- **Cmd/Ctrl+L** - Load session
- **Cmd/Ctrl+E** - Export WebVTT
- **Space** - Play/Pause audio
- **M** - Add caption
- **←/→** - Skip 5 seconds
- **Shift+←/→** - Skip 1 second

## License

MIT License - Copyright (c) 2025 Northwestern University
Developed by Sophia Francis

## Support

For issues or questions, refer to the README in the Help menu of the application.