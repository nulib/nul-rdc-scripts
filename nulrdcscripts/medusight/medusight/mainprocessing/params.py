"""
Command-line argument parsing for medusight
Works in both CLI and GUI (Eel) contexts
"""

import argparse
import sys

def get_parser():
    """Create and return the argument parser"""
    parser = argparse.ArgumentParser(
        description="Video Quality Control Analysis Tool"
    )
    
    parser.add_argument(
        '--input', '-i',
        dest='input_path',
        required=True,
        help='Input file or folder path'
    )
    
    parser.add_argument(
        '--output',
        dest='output_path',
        default='input',
        help='Output directory (default: same as input)'
    )
    
    parser.add_argument(
        '--videobitdepth',
        choices=['10', '10bit', '10Bit', '8', '8bit', '8Bit'],
        default='10',
        help='Video bit depth (default: 10)'
    )
    
    parser.add_argument(
        '--crop-mode',
        choices=['auto', 'combined', 'headswitching', 'off', 'none', 'manual'],
        default='auto',
        help='Crop detection mode (default: auto)'
    )
    
    parser.add_argument(
        '--manual-crop',
        type=str,
        default=None,
        help='Manual crop values (format: w:h:x:y)'
    )
    
    parser.add_argument(
        '--sample-interval',
        type=int,
        default=30,
        help='Sample interval for crop detection in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--analyze-audio',
        action='store_true',
        default=False,
        help='Perform audio quality analysis'
    )
    
    parser.add_argument(
        '--audio-standard',
        choices=['broadcast', 'streaming', 'film'],
        default='broadcast',
        help='Audio quality standard (default: broadcast)'
    )
    
    parser.add_argument(
        '--target-lufs',
        type=float,
        default=None,
        help='Target LUFS level (overrides standard)'
    )
    
    parser.add_argument(
        '--max-true-peak',
        type=float,
        default=None,
        help='Maximum true peak level in dBTP (overrides standard)'
    )
    
    return parser


# Create a default args object for GUI mode
class DefaultArgs:
    """Default arguments for GUI/non-CLI usage"""
    def __init__(self):
        self.input_path = None
        self.output_path = 'input'
        self.videobitdepth = '10'
        self.crop_mode = 'auto'
        self.manual_crop = None
        self.sample_interval = 30
        self.analyze_audio = False
        self.audio_standard = 'broadcast'
        self.target_lufs = None
        self.max_true_peak = None


# Determine if we're running as CLI or being imported by GUI
# Check if we're being run as __main__ or if there are actual CLI args
if __name__ == '__main__' or (len(sys.argv) > 1 and '--input' in sys.argv):
    # CLI mode - parse actual arguments
    parser = get_parser()
    args = parser.parse_args()
else:
    # GUI mode - use defaults (will be overridden by GUI)
    args = DefaultArgs()