# MeduSight

**Video Quality Control & Analysis Tool**

A comprehensive video quality control analysis tool that serves as a complete alternative to QCTools for broadcast and archival standards compliance.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey)]()

---

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [System Requirements](#system-requirements)
- [Configuration](#configuration)
- [Building from Source](#building-from-source)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## 🎯 About

MeduSight provides automated video quality control analysis for broadcast and archival workflows. It processes QCTools XML files and raw video files to identify quality issues, generate comprehensive reports, and ensure compliance with industry standards.

**Version Date:** 8-8-25  
**Developed by Sophia Francis**  
Northwestern University

---

## ✨ Features

> **Note:** Features marked with 🚧 are currently under construction and not yet functional. MeduSight currently supports QCTools XML/JSON processing with full video quality analysis.

### Video Analysis
- **QCTools XML/JSON Processing** - Analyze externally preprocessed QCTools data
- **Direct Video Processing** - 🚧 Under Construction (Extract statistics directly from video files)
- **Intelligent Crop Detection** - 🚧 Under Construction (Automatic black border and headswitching noise removal)
- **Multi-threaded Batch Processing** - Process multiple files simultaneously

### Quality Standards
- **10-bit and 8-bit Video Support** - Automatic bit depth detection
- **Broadcast Range Compliance** - ITU-R BT.601/709 standards validation
- **Y/U/V Channel Analysis** - Comprehensive luma and chroma checking
- **Saturation Detection** - Illegal, clipping, and broadcast range thresholds

### Audio Analysis
- **EBU R128 Loudness Analysis** - 🚧 Under Construction (LUFS, true peak, and loudness range measurements)
- **Multiple Standards** - 🚧 Under Construction (Broadcast/Streaming/Film standards)
- **Silence Detection** - 🚧 Under Construction (Identify audio dropouts)
- **Normalization Recommendations** - 🚧 Under Construction (Automated gain adjustment suggestions)

### Reporting
- **Video-Level Reports** - Summary statistics and pass/fail status
- **Frame-Level Reports** - Detailed failing frame timestamps (HH:MM:SS.mmm)
- **Audio Quality Reports** - 🚧 Under Construction
- **CSV Export** - Raw data and summary statistics

### User Interface
- **Modern Desktop GUI** - Clean, accessible interface with dark mode
- **Colorblind Mode** - Yellow/blue color scheme for accessibility
- **High Contrast Mode** - Enhanced visibility option
- **Batch Processing** - Drag and drop multiple files or folders

---

## 💾 Installation

### Windows

1. Download `MeduSight-Setup-Windows.exe` from the [Releases](https://github.com/northwestern/medusight/releases) page
2. Run the installer
3. Follow the installation wizard
4. Launch MeduSight from the Start Menu or Desktop shortcut

### macOS

1. Download `MeduSight.dmg` from the [Releases](https://github.com/northwestern/medusight/releases) page
2. Open the DMG file
3. Drag **MeduSight** to your **Applications** folder
4. Launch from Applications (you may need to allow the app in System Preferences → Security & Privacy)

---

## 🚀 Usage

### GUI Mode (Recommended)

1. **Launch MeduSight** application
2. **Select XML Files Mode** (Video Files mode is under construction)
3. **Select Files or Folders**
   - Click the upload area to browse
   - Or use the manual path input as a fallback
4. **Click "Process Files"**
5. **Review Reports**
   - Video-level summary
   - Frame-level details

### Command Line Interface (CLI)

#### Single File Processing

```bash
# Basic usage
poetry run medu --input example.xml

# Short form
poetry run medu -i /files/example.xml

# Specify output directory
poetry run medu --input video.mkv.qctools.xml --output ./reports

# With video bit depth
poetry run medu -i video.xml --videobitdepth 10
```

#### Batch Processing

```bash
# Process entire folder of XML files
poetry run medu --input /path/to/xml_files --output ./reports

# Specify bit depth
poetry run medu --input /xml_folder --videobitdepth 10
```

#### Advanced Options (🚧 Under Construction)

The following options are planned but not yet functional:

```bash
# Video processing with crop detection (coming soon)
poetry run medu -i video.mkv --crop-mode combined

# Audio analysis (coming soon)
poetry run medu -i video.mkv --analyze-audio --audio-standard broadcast
```

### Processing QCTools XML (Current Functionality)

```bash
# 1. Generate QCTools XML (external tool required)
qcli-qt -i video.mkv -o video.mkv.qctools.xml

# 2. Process in MeduSight
poetry run medu --input video.mkv.qctools.xml
```

### Direct Video Processing (🚧 Under Construction)

```bash
# Direct video processing without QCTools (coming soon)
poetry run medu --input video.mkv --crop-mode auto --analyze-audio
```

---

## 💻 System Requirements

### Minimum Requirements
- **Windows:** 10/11 (64-bit) or **macOS:** 10.14+
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB for application, additional space for processing
- **FFmpeg:** Bundled with installer (required for direct video processing)

### Software Dependencies
- **Python:** 3.12+ (for source installation)
- **Poetry:** Package manager (for source installation)
- **QCTools:** Required for XML preprocessing (current workflow)
- **FFmpeg:** 🚧 For future direct video processing (under construction)

### Required Python Packages
See `pyproject.toml` for complete list. Key dependencies:
- pandas
- lxml
- progressbar2
- tabulate
- eel (for GUI)

---

## ⚙️ Configuration

### Changing Value Ranges

Quality control thresholds are defined in CSV files located in `medusight/mainprocessing/data/`:

- `Video8BitValues.csv` - Standards for 8-bit video
- `Video10BitValues.csv` - Standards for 10-bit video

**⚠️ Warning:** These CSVs are used in equations throughout the codebase. Modifying them requires careful consideration of the impact on analysis logic. Changes should only be made if you understand the broadcast standards being implemented.

#### CSV Structure

```csv
criteria,brngout,clipping,avglow,avghigh,brnglimit,clippinglimit,illegal,ideal,max
ymin,63,0,,,,,,,
ymax,941,1023,,,,,,,
sat,,,,,354.8,472.8,724.08,,
```

- **brngout:** Broadcast range outer limit
- **clipping:** Clipping threshold
- **brnglimit, clippinglimit, illegal:** Saturation thresholds

---

## 🔨 Building from Source

### Prerequisites

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clone repository
git clone https://github.com/northwestern/medusight.git
cd medusight

# Install dependencies
poetry install
```

### Building Executables

#### Cross-Platform Build Script

```bash
# Build for current platform
poetry run python build.py

# Output:
# Windows: dist/MeduSight.exe + installer/MeduSight-Setup-Windows.exe
# macOS: dist/MeduSight.app + dist/MeduSight.dmg
```

#### Manual Build (PyInstaller)

```bash
# Generate spec file and build
poetry run pyinstaller medusight.spec --clean

# Or build directly
poetry run pyinstaller app/app.py \
  --name MeduSight \
  --icon app/icon.ico \
  --windowed \
  --onefile
```

### Platform-Specific Notes

#### Windows
- Install [Inno Setup](https://jrsoftware.org/isdl.php) for installer creation
- Icon format: `.ico` (created automatically by build script)

#### macOS
- Install dmgbuild: `poetry add --group dev dmgbuild`
- Icon format: `.icns` (created automatically by build script)
- May need to sign/notarize for distribution outside App Store

---

## 🙏 Acknowledgments

### Contributors

Many thanks to the following contributors who helped make MeduSight possible:

- **Alec Bertoy**
- **Dan Zellner**
- **Sarah Hartzell**
- **Morgan Morel**
- **Brendan Coates**
- **Ben Turkus**

### Reference Materials

This project was developed with guidance from:

- _Python for Data Analytics_ - Wes McKinney
- _Python Data Analytics: With Pandas, NumPy, and Matplotlib_ - Fabio Nelli
- _Practical Python Data Wrangling and Data Quality_ - Susan E. McGregor
- _Data Wrangling with Python_ - Jacqueline Kazil, Katharine Jarmul
- [How to convert an XML file to python pandas dataframe](https://www.youtube.com/watch?v=WWgiRkvl1Ws) - Paris Nakita Kejser

---

## 📄 License

MIT License

Copyright © 2025 Northwestern University

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Developed by Sophia Francis at Northwestern University.**

---

## 📞 Support

For issues, questions, or contributions, please visit the [GitHub Issues](https://github.com/northwestern/medusight/issues) page.

---

**MeduSight** - Professional video quality control made accessible.