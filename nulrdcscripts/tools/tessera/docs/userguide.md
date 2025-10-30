# Tessera User Guide

**WebVTT Caption Editor for Classical Music Archival**

Welcome to Tessera! This guide will walk you through creating WebVTT caption files for classical music recordings.

---

## Memory Protection & Large Files

Tessera is designed to work with preservation-quality audio files, which can be very large (often 2GB+ for uncompressed WAV files). To protect your work and system performance, Tessera includes automatic memory management.

### Understanding the Protections

#### Large File Warning (>2GB)

When you try to load a file larger than 2GB, you'll see a confirmation dialog:

```
This file is [size] MB, which may cause performance issues. Continue?
```

- Click **OK** to proceed with loading the file
- Click **Cancel** to choose a different file

**This is just a warning** - you can still work with the file, but be aware it may slow down your system.

#### 3-Hour Session Timeout

Tessera automatically monitors two things:
1. **Total session time**: How long you've had the application open
2. **Total audio loaded**: Combined size of all audio files loaded this session

When **EITHER** of these conditions is met:
- Session has been open for **3+ hours**, OR
- You've loaded **3+ GB** of total audio files

Tessera will trigger its memory protection system.

### What Happens During Memory Protection

#### Step 1: Automatic Save

Before showing you any warning, Tessera automatically saves your work as:
```
tessera_autosave_session.json
```

This file is downloaded to your default downloads folder. **Your work is safe!**

#### Step 2: Warning Dialog

You'll see a dialog that says:

```
💾 Auto-Save Complete!

Your session has been automatically saved as:
"tessera_autosave_session.json"

⚠️ MEMORY WARNING ⚠️
To prevent performance issues and potential data loss, 
this application will automatically close in 2 minutes.

Click OK to close now, or Cancel to continue working.
(Application will close automatically in 2 minutes if you continue working)
```

**You have two choices:**

**Option A: Click OK**
- Application closes immediately
- Your work is saved
- Recommended for best performance

**Option B: Click Cancel**
- You get 2 more minutes to finish up
- Countdown alerts at 1 minute, 30 seconds, and 10 seconds
- Application closes automatically after 2 minutes

### Resuming Your Work

After the application closes:

1. **Reopen Tessera**
2. **Click "Load Session"**
3. **Select your `tessera_autosave_session.json` file**
4. All your captions and context will be restored
5. **Reload your audio file** (audio files are not saved in sessions)
6. Continue working with fresh memory

### Why This System Exists

**Preservation-quality audio files are huge:**
- Uncompressed WAV files: 100MB - 5GB+
- Multiple files in one session compounds the problem
- Browser memory limitations can cause crashes

**The auto-close system prevents:**
- Application freezing or crashing
- System slowdowns
- Data loss from memory-related crashes
- Forcing you to manually restart

### Working With Very Large Files

#### Single Large File (>2GB)

If you're working with one very large file:
- You'll get the warning when loading
- Save your session every 15-20 minutes
- The 3-hour timeout will still apply

#### Multiple Large Files

If you're processing multiple preservation files:
- Work on one file at a time when possible
- Save your session after each file
- Close and reopen Tessera between files to clear memory
- Load saved sessions to continue

#### Marathon Sessions

If you need to work for more than 3 hours straight:
- The application will force a break
- This is actually good for you! Take a moment to:
  - Stretch
  - Rest your eyes
  - Get water
- Reopen and load your session
- Continue working with better focus

### Memory Tips (Even Without Warnings)

**For optimal performance:**

1. **Close and reopen regularly**: Even if you don't get a warning, closing and reopening every 2-3 hours keeps memory fresh

2. **Save frequently**: Use Ctrl/Cmd+S to save sessions every 10-15 minutes

3. **One file at a time**: If possible, complete captions for one recording before moving to the next

4. **Check your system**: If your computer has limited RAM (<8GB), be extra cautious with large files

5. **Monitor performance**: If Tessera starts feeling sluggish, save and restart before the auto-close kicks in

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Workflow](#basic-workflow)
3. [Setting Piece Context](#setting-piece-context)
4. [Adding Movement Captions](#adding-movement-captions)
5. [Using Override Fields](#using-override-fields)
6. [Managing Your Work](#managing-your-work)
7. [Memory Protection & Large Files](#memory-protection--large-files)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [Tips & Best Practices](#tips--best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Launching Tessera

Double-click the Tessera application icon to launch. The main window will open with four main sections:

1. **Audio Player** (top) - Load and control audio playback
2. **Piece Context** (left side) - Set metadata for the piece
3. **Add Caption** (center) - Create individual movement captions
4. **Output** (right side) - View generated WebVTT and preview

### Understanding the Interface

- **Theme Selector** (top-right) - Choose from multiple color themes for accessibility
- **Menu Button** (hamburger icon) - Access README and license information
- **Caption Count** - Shows how many captions you've created

---

## Basic Workflow

Follow these steps for each recording:

1. **Load audio file** → Click the upload area or drag & drop
2. **Set piece context** → Click "Edit Piece Context" 
3. **Add captions** → Mark timestamps for each movement
4. **Export WebVTT** → Save your completed caption file

---

## Setting Piece Context

Before adding captions, you must set the piece context. This information will be included in every caption.

### Required Fields

- **Title**: Full title of the work (e.g., "Symphony No. 5 in C minor, Op. 67")
- **Performers**: Primary performing ensemble (e.g., "Chicago Symphony Orchestra")

### Optional Fields

- **Date**: Performance date (e.g., "March 15, 2024")
- **Conductor**: Conductor name (e.g., "Riccardo Muti")
- **Composer**: Composer name (e.g., "Ludwig van Beethoven")
- **Additional Info**: Any other relevant context

### How to Set Context

1. Click the **"Edit Piece Context"** button
2. Fill in the required fields (Title and Performers)
3. Add optional fields as available
4. Click **"Save Context"**

The context will now display in the left panel and will be applied to all captions you create.

---

## Adding Movement Captions

Once your audio is loaded and context is set, you're ready to add captions for each movement.

### Step-by-Step Process

1. **Play the audio** - Use the built-in audio player controls
2. **Note the start time** - When a movement begins, the current timestamp appears in the time display
3. **Fill in the form**:
   - **Movement Name**: Name of the movement (e.g., "I. Allegro con brio")
   - **Start Time**: Beginning timestamp (auto-filled from current playback position)
   - **End Time**: Ending timestamp (auto-filled as 5 seconds after start)
4. **Add Notes** (optional): Internal notes for your reference (not included in WebVTT)
5. **Click "Add Caption"**

### Time Format

All times use the format: `HH:MM:SS.mmm`
- Hours: 2 digits (00-99)
- Minutes: 2 digits (00-59)
- Seconds: 2 digits (00-59)
- Milliseconds: 3 digits (000-999)

**Example**: `00:03:45.250` = 3 minutes, 45.25 seconds

### Editing Captions

- Click the **✏️ (edit)** button next to any caption
- The caption data will populate the form
- Make your changes and click "Add Caption" again
- The original caption will be removed

### Deleting Captions

- Click the **✕ (delete)** button next to any caption
- Confirm the deletion when prompted

---

## Using Override Fields

Sometimes you need to override the piece context for specific movements. Common scenarios:

### When to Use Overrides

- **Multiple pieces on one recording**: Different performers for each piece
- **Guest artists**: A soloist joins for one movement
- **Different performance dates**: Movements recorded on different dates

### How to Use Overrides

1. In the "Add Caption" section, click **"Override Details"** to expand
2. Fill in any fields you want to override:
   - Override Performers
   - Override Date
   - Override Conductor
3. These values will be used ONLY for this caption
4. Empty override fields will use the piece context values

### Example

**Piece Context:**
- Performers: Chicago Symphony Orchestra
- Conductor: Riccardo Muti

**Override for one movement:**
- Override Performers: "Chicago Symphony Orchestra with Yo-Yo Ma, Cello"

Result: That movement's caption will show the guest artist while others use the main performers.

---

## Managing Your Work

### Saving Your Session

**Why save sessions?**
- Work in progress that isn't finished
- Come back to a project later
- Backup before making major changes

**How to save:**
- Click **"Save Session"** button, or
- Use keyboard shortcut: **Ctrl+S** (Windows/Linux) or **Cmd+S** (Mac)
- Choose a location and filename (`.json` file)

**What's saved:**
- Piece context
- All captions
- Notes

**What's NOT saved:**
- The audio file itself (you'll need to reload it)
- Theme preference (stored separately)

### Loading a Session

1. Click **"Load Session"** button
2. Select your `.json` session file
3. All your captions and context will be restored
4. Reload your audio file to continue working

### Exporting WebVTT

When your captions are complete:

1. Review the **VTT Output** tab to verify
2. Click **"Export VTT"** button, or
3. Use keyboard shortcut: **Ctrl+E** (Windows/Linux) or **Cmd+E** (Mac)
4. Save the `.vtt` file with your audio

### Sorting Captions

Click **"Sort by Time"** to reorder all captions chronologically by start time. This is useful if you added captions out of order.

### Clearing All Captions

Click **"Clear All"** to remove all captions while preserving your piece context. Use this to start fresh with a new recording that uses the same performers.

---

## Keyboard Shortcuts

### Audio Playback Controls

| Keys | Skip Amount | Use Case |
|------|-------------|----------|
| **Space** or **K** | Play/Pause | Toggle audio playback |
| **←/→** | **1 second** | Default navigation |
| **Shift+←/→** | **0.1 seconds** (100ms) | Fine-tuning timestamps |
| **Ctrl+←/→** | **5 seconds** | Quick browsing |
| **,/.** | **0.033 seconds** (~1 frame) | Frame-by-frame precision |
| **J/L** | **10 seconds** | Jumping between sections |
| **↑/↓** | Volume | Increase/decrease volume 10% |
| **M** | Mute/Unmute | Toggle audio mute |
| **I** | Mark Start | Insert current time as Start Time |
| **O** | Mark End | Insert current time as End Time |

### Application Controls

| Shortcut | Action |
|----------|--------|
| **Ctrl/Cmd + S** | Save session |
| **Ctrl/Cmd + E** | Export WebVTT file |
| **Ctrl/Cmd + O** | Load session |
| **ESC** | Close modals and dropdowns |

### Efficient Workflow with Keyboard Shortcuts

For finding exact movement starts in classical recordings:

1. **Play through** to find approximate start location
2. Press **J** to jump back 10 seconds before the start
3. Use **→** (1 second) to get close to the exact moment
4. Use **Shift+→** (0.1 second) to fine-tune
5. Use **,/.** for frame-perfect precision if needed
6. Press **I** to mark the exact start time
7. Continue playing to the end of the movement
8. Press **O** to mark the end time
9. Fill in movement name and press **Add Caption**

**Tip**: Audio shortcuts only work when you're NOT typing in a text field. If a shortcut doesn't work, click outside the input fields first.

---

## Tips & Best Practices

### For Classical Music Cataloging

1. **Use full, formal names**
   - ✅ "Symphony No. 5 in C minor, Op. 67"
   - ❌ "Beethoven 5th"

2. **Include movement markings in original language**
   - ✅ "I. Allegro con brio"
   - ❌ "First Movement - Fast"

3. **Be consistent with performer names**
   - Use the same format throughout
   - Match program notes when available

4. **Date formatting**
   - Be consistent: "March 15, 2024" or "2024-03-15"
   - Include dates when known

### Workflow Efficiency

1. **Listen through first** - Note approximate movement timestamps before adding captions
2. **Use the audio player** - Play, pause, and scrub to find exact timestamps
3. **Work chronologically** - Add movements in order from beginning to end
4. **Save frequently** - Save sessions every 10-15 minutes
5. **Review before export** - Check the Preview tab to see how captions are grouped

### Quality Control

- **Verify timestamps**: Ensure end time is after start time
- **Check for gaps**: Review the Preview to spot missing movements
- **Proofread metadata**: Double-check composer and performer spellings
- **Test the output**: Load the WebVTT file in a video player to verify timing

---

## Troubleshooting

### Audio won't load

**Problem**: "Error loading audio file" message  
**Solutions**:
- Check file format (supported: MP3, WAV, OGG, M4A)
- Try a different audio file
- Ensure file isn't corrupted
- **For files >2GB**: Confirm you want to proceed when asked
- Check available system memory (close other applications)

### Application closes unexpectedly

**Problem**: Tessera closes automatically  
**This is normal!** See [Memory Protection & Large Files](#memory-protection--large-files) section.

**What happened**:
- You've been working for 3+ hours, OR
- You've loaded 3+ GB of audio files
- Your work was automatically saved as `tessera_autosave_session.json`

**What to do**:
1. Reopen Tessera
2. Click "Load Session"
3. Select the autosave file
4. Reload your audio file
5. Continue working

### Memory warning appears

**Problem**: "Memory Warning" dialog appears  
**This is a safety feature!** Your work has been automatically saved.

**Recommended action**:
1. Click **OK** to close immediately (recommended)
2. Reopen Tessera
3. Load your autosaved session
4. Continue with fresh memory

**If you need 2 more minutes**:
1. Click **Cancel**
2. Finish your current task quickly
3. Application will close automatically
4. Your work is already saved

### Can't add caption

**Problem**: "Please set piece context first"  
**Solution**: Click "Edit Piece Context" and fill in Title and Performers

**Problem**: "Start and end times are required"  
**Solution**: Both time fields must be filled in

**Problem**: "End time must be after start time"  
**Solution**: Check that your end time is later than start time

**Problem**: "Invalid time format"  
**Solution**: Use format HH:MM:SS.mmm (e.g., 00:03:45.250)

### Session won't load

**Problem**: "Error loading session file"  
**Solutions**:
- Ensure it's a valid JSON file from Tessera
- Check that file isn't corrupted
- Try a different session file

### Captions appear out of order

**Solution**: Click "Sort by Time" to reorder chronologically

### WebVTT export shows wrong information

**Check**:
- Piece context is correct
- Override fields aren't accidentally filled in
- All captions use consistent formatting

### Theme or settings won't save

**Note**: Theme preference is saved in browser storage. If using multiple computers, you'll need to set theme on each device.

---

## Support

For technical issues, feature requests, or questions:

- Contact: Northwestern University Digital Services
- Check the README for technical documentation
- Report bugs via the issue tracker

---

## Appendix: WebVTT Format Reference

Tessera generates WebVTT files that look like this:

```
WEBVTT

00:00:15.000 --> 00:05:23.000
Symphony No. 5 in C minor, Op. 67. I. Allegro con brio. Chicago Symphony Orchestra. Riccardo Muti, Conductor. March 15, 2024

00:05:24.000 --> 00:12:45.000
Symphony No. 5 in C minor, Op. 67. II. Andante con moto. Chicago Symphony Orchestra. Riccardo Muti, Conductor. March 15, 2024
```

Each caption includes:
- Title
- Movement name (if provided)
- Performers
- Conductor (if provided)
- Date (if provided)

All fields are separated by periods for readability.

---

**Northwestern University Libraries**  
**Data Curation, a division of Academic Innovation**

*Last updated: 2025*
