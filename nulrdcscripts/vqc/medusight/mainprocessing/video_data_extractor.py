import subprocess
import pandas as pd
import os
import argparse
from collections import Counter
import numpy as np


def analyze_region_saturation(video_path, crop_value, sample_frames=30):
    """
    Analyze saturation for a specific crop/region.
    
    Args:
        video_path: Path to video file
        crop_value: Crop string like "1920:1080:0:0" or None for full frame
        sample_frames: Number of frames to sample for analysis
        
    Returns:
        dict with saturation statistics
    """
    # FFmpeg movie filter on Windows needs special handling
    # Instead of using lavfi with movie filter, use direct file input with filter_complex
    
    # Build filter chain
    if crop_value:
        filter_chain = f"[0:v]crop={crop_value},select='not(mod(n\\,30))',signalstats[out]"
    else:
        filter_chain = f"[0:v]select='not(mod(n\\,30))',signalstats[out]"
    
    cmd = [
        'ffprobe',
        '-i', video_path,  # Use -i for input instead of lavfi movie
        '-filter_complex', filter_chain,
        '-map', '[out]',
        '-show_entries', 
        'frame_tags=lavfi.signalstats.SATMAX,lavfi.signalstats.SATAVG',
        '-of', 'csv=p=0',
        '-v', 'quiet'
    ]
    
    cmd = [
        'ffprobe',
        '-f', 'lavfi',
        '-i', lavfi_input,
        '-show_entries', 
        'frame_tags=lavfi.signalstats.SATMAX,lavfi.signalstats.SATAVG',
        '-of', 'csv=p=0',
        '-v', 'quiet'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60
        )
        
        # Parse saturation values
        sat_values = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(',')
                if len(parts) >= 2:
                    try:
                        sat_max = float(parts[0]) if parts[0] else 0
                        sat_avg = float(parts[1]) if parts[1] else 0
                        sat_values.append({'max': sat_max, 'avg': sat_avg})
                    except:
                        pass
        
        if not sat_values:
            return None
        
        # Calculate statistics
        max_values = [s['max'] for s in sat_values]
        avg_values = [s['avg'] for s in sat_values]
        
        return {
            'sat_max_mean': np.mean(max_values),
            'sat_max_std': np.std(max_values),
            'sat_max_95th': np.percentile(max_values, 95),
            'sat_avg_mean': np.mean(avg_values),
            'sample_count': len(sat_values)
        }
        
    except Exception as e:
        print(f"Error analyzing region: {e}")
        return None


def detect_headswitching_crop(video_path, base_crop=None, test_heights=[0, 10, 20, 30, 40, 50, 60], 
                               sample_interval=30):
    """
    Detect headswitching noise by comparing bottom-edge saturation across different crop heights.
    
    Strategy:
    1. Test progressively aggressive bottom crops (removing 0, 10, 20... pixels from bottom)
    2. Analyze saturation for each crop candidate
    3. Find the crop height where saturation drops significantly
    4. That indicates we've excluded the headswitching noise
    
    Args:
        video_path: Path to video file
        base_crop: Starting crop (e.g., from black border detection) - format "W:H:X:Y"
                   If None, uses full frame dimensions
        test_heights: List of pixel heights to test cropping from bottom
        sample_interval: Frame sampling rate (every Nth frame)
        
    Returns:
        Crop string that excludes headswitching, or None if no headswitching detected
    """
    print(f"Detecting headswitching noise for: {video_path}")
    if base_crop:
        print(f"Starting from base crop: {base_crop}")
    print("Testing different bottom crop heights...")
    
    # Get dimensions - either from base_crop or probe the video
    if base_crop:
        # Parse base crop: "width:height:x:y"
        parts = base_crop.split(':')
        width = int(parts[0])
        height = int(parts[1])
        x_offset = int(parts[2])
        y_offset = int(parts[3])
        print(f"Using base crop dimensions: {width}x{height} at offset ({x_offset},{y_offset})")
    else:
        # Probe video for full dimensions
        probe_cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=p=0',
            video_path
        ]
        
        try:
            result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
            width, height = map(int, result.stdout.strip().split(','))
            x_offset = 0
            y_offset = 0
            print(f"Video dimensions: {width}x{height}")
        except Exception as e:
            print(f"Error getting video dimensions: {e}")
            return None
    
    # Test different crop heights
    results = []
    for crop_height in test_heights:
        if crop_height >= height:
            continue
            
        if crop_height == 0:
            # Use base crop (or full frame if no base crop)
            if base_crop:
                crop_value = base_crop
                print(f"\nTesting: Base crop ({width}x{height})")
            else:
                crop_value = None
                print(f"\nTesting: Full frame ({width}x{height})")
        else:
            # Crop additional pixels from bottom
            new_height = height - crop_height
            crop_value = f"{width}:{new_height}:{x_offset}:{y_offset}"
            print(f"\nTesting: Remove {crop_height}px from bottom ({width}x{new_height})")
        
        stats = analyze_region_saturation(video_path, crop_value)
        
        if stats:
            results.append({
                'crop_height': crop_height,
                'crop_value': crop_value,
                'sat_max_mean': stats['sat_max_mean'],
                'sat_max_95th': stats['sat_max_95th'],
                'sat_avg_mean': stats['sat_avg_mean']
            })
            print(f"  Sat Max Mean: {stats['sat_max_mean']:.1f}, 95th: {stats['sat_max_95th']:.1f}")
    
    if len(results) < 2:
        print("\nInsufficient data for headswitching detection")
        return base_crop  # Return base crop if we can't detect headswitching
    
    # Analyze results to find optimal crop
    print("\n=== Analysis ===")
    
    # Look for significant drop in saturation when cropping bottom
    baseline_sat = results[0]['sat_max_mean']  # Base crop (or full frame) saturation
    
    for i, result in enumerate(results[1:], 1):
        sat_reduction = baseline_sat - result['sat_max_mean']
        reduction_pct = (sat_reduction / baseline_sat * 100) if baseline_sat > 0 else 0
        
        print(f"Crop {result['crop_height']}px: {reduction_pct:.1f}% saturation reduction")
        
        # If we see >15% saturation reduction, that's likely removing headswitching
        if reduction_pct > 15:
            print(f"\n✓ Headswitching detected! Recommend cropping {result['crop_height']}px from bottom")
            print(f"  Crop value: {result['crop_value']}")
            return result['crop_value']
    
    # If no significant reduction found, probably no headswitching
    print("\n✓ No significant headswitching detected")
    return base_crop if base_crop else None


def detect_crop(video_path, use_most_frequent=True, sample_interval=900):
    """
    Detect crop value in a video.
    
    Args:
        video_path: Path to the video file
        use_most_frequent: If True, returns most frequent crop (handles headswitching).
                          If False, returns first detected crop (faster, simpler).
        sample_interval: Frame interval for sampling (900 = every 30 seconds at 30fps)
                        Lower = more accurate but slower
                        Set to 1 for every frame (slow but most accurate)
    
    Returns:
        Crop string like "1920:1080:0:0" or None if detection fails
    """
    print(f"Detecting crop for: {video_path}")
    
    # Build cropdetect command with sampling
    if sample_interval > 1:
        vf = f"select='not(mod(n\\,{sample_interval}))',cropdetect=24:16:0"
    else:
        vf = "cropdetect=24:16:0"
    
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', vf,
        '-f', 'null',
        '-'
    ]
    
    try:
        # Run ffmpeg and capture stderr (where crop info is printed)
        result = subprocess.run(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Extract all crop values from output
        crop_values = []
        for line in result.stderr.split('\n'):
            if 'crop=' in line:
                # Extract crop value like "crop=1920:1080:0:0"
                start = line.find('crop=')
                if start != -1:
                    crop_str = line[start:].split()[0]  # Get first word after crop=
                    crop_values.append(crop_str)
        
        if not crop_values:
            print("Warning: No crop values detected, video may not need cropping")
            return None
        
        if use_most_frequent:
            # Find most frequent crop value (handles headswitching)
            crop_counter = Counter(crop_values)
            most_common_crop = crop_counter.most_common(1)[0]
            crop_value = most_common_crop[0].replace('crop=', '')
            frequency = most_common_crop[1]
            
            print(f"Most frequent crop: {crop_value} (detected {frequency}/{len(crop_values)} times)")
            print(f"Total unique crops detected: {len(crop_counter)}")
            
            return crop_value
        else:
            # Return first detected crop (simpler, no headswitching protection)
            crop_value = crop_values[0].replace('crop=', '')
            print(f"First detected crop: {crop_value}")
            print(f"Total crops detected: {len(crop_values)}")
            
            return crop_value
        
    except subprocess.TimeoutExpired:
        print("Error: Crop detection timed out")
        return None
    except Exception as e:
        print(f"Error during crop detection: {e}")
        return None


def extract_video_stats_cropped(video_path, crop_value=None, output_csv=None):
    """
    Extract frame-by-frame video statistics using ffprobe with optional cropping.
    Uses direct file input instead of lavfi movie filter to avoid Windows path issues.
    
    Args:
        video_path: Path to the video file
        crop_value: Crop string like "1920:1080:0:0" (or None for no crop)
        output_csv: Optional path to save CSV (if None, returns DataFrame only)
    
    Returns:
        pandas DataFrame with columns matching QCTools format
    """
    print(f"Extracting video statistics from: {video_path}")
    if crop_value:
        print(f"Applying crop: {crop_value}")
    
    # Build filter chain using filter_complex instead of lavfi movie
    if crop_value:
        filter_chain = f"[0:v]crop={crop_value},signalstats[out]"
    else:
        filter_chain = "[0:v]signalstats[out]"
    
    # Build ffprobe command using -i input and -filter_complex
    cmd = [
        'ffprobe',
        '-i', video_path,  # Direct file input - Windows paths work here
        '-filter_complex', filter_chain,
        '-map', '[out]',
        '-show_entries', 
        'frame=pts_time:frame_tags=lavfi.signalstats.YMIN,lavfi.signalstats.YMAX,lavfi.signalstats.YLOW,lavfi.signalstats.YHIGH,lavfi.signalstats.YAVG,lavfi.signalstats.UMIN,lavfi.signalstats.UMAX,lavfi.signalstats.ULOW,lavfi.signalstats.UHIGH,lavfi.signalstats.UAVG,lavfi.signalstats.VMIN,lavfi.signalstats.VMAX,lavfi.signalstats.VLOW,lavfi.signalstats.VHIGH,lavfi.signalstats.VAVG,lavfi.signalstats.SATMAX',
        '-of', 'csv=p=0'
    ]
    
    try:
        # Run ffprobe
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        # Parse CSV output
        # Column names to match QCTools/existing analysis code
        column_names = [
            'Frame Time',  # pts_time
            'ymin',
            'ymax', 
            'ylow',
            'yhigh',
            'yavg',
            'umin',
            'umax',
            'ulow',
            'uhigh',
            'uavg',
            'vmin',
            'vmax',
            'vlow',
            'vhigh',
            'vavg',
            'satmax'  # SATMAX in signalstats
        ]
        
        # Create DataFrame from CSV output
        from io import StringIO
        df = pd.read_csv(StringIO(result.stdout), names=column_names)
        
        # Convert Frame Time to float
        df['Frame Time'] = pd.to_numeric(df['Frame Time'], errors='coerce')
        
        # Convert all stat columns to numeric
        for col in column_names[1:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Rename satmax to sathigh for consistency with analysis code expectations
        df.rename(columns={'satmax': 'sathigh'}, inplace=True)
        
        print(f"Extracted {len(df)} frames of data")
        
        # Save to CSV if requested
        if output_csv:
            df.to_csv(output_csv, index=False)
            print(f"Saved to: {output_csv}")
        
        return df
        
    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error extracting video stats: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_video_with_options(video_path, output_dir=None, crop_mode='auto', 
                                manual_crop=None, sample_interval=900):
    """
    Complete workflow with flexible cropping options.
    
    Args:
        video_path: Path to video file
        output_dir: Optional directory to save CSV output
        crop_mode: Cropping behavior:
                   - 'auto': Auto-detect black borders only (most frequent)
                   - 'combined': Black borders + headswitching (two-step detection)
                   - 'headswitching': Headswitching noise only (no black border detection)
                   - 'off' or 'none': No cropping applied
                   - 'manual': Use manual_crop parameter
        manual_crop: Manual crop string like "1920:1080:0:0" (used when crop_mode='manual')
        sample_interval: Frame sampling interval for auto-detection (default 900)
    
    Returns:
        pandas DataFrame with video statistics
    """
    crop_value = None
    
    # Determine crop based on mode
    if crop_mode == 'combined':
        print("=== COMBINED MODE: Black borders + Headswitching detection ===")
        
        # Step 1: Detect black borders
        print("\n--- Step 1: Detecting black borders ---")
        base_crop = detect_crop(video_path, 
                                use_most_frequent=True,
                                sample_interval=sample_interval)
        
        # Step 2: Detect headswitching from the base crop
        print("\n--- Step 2: Detecting headswitching noise ---")
        crop_value = detect_headswitching_crop(video_path, base_crop=base_crop)
        
        print(f"\n=== FINAL CROP: {crop_value} ===")
        
    elif crop_mode == 'headswitching':
        print("Using saturation-based headswitching detection (no black border detection)...")
        crop_value = detect_headswitching_crop(video_path, base_crop=None)
        
    elif crop_mode == 'auto':
        print("Auto-detecting black borders (most frequent)...")
        crop_value = detect_crop(video_path, 
                                 use_most_frequent=True,
                                 sample_interval=sample_interval)
    elif crop_mode == 'manual':
        if manual_crop:
            print(f"Using manual crop: {manual_crop}")
            crop_value = manual_crop
        else:
            print("Warning: Manual crop mode selected but no crop value provided")
    elif crop_mode in ['off', 'none']:
        print("Crop disabled - processing full frame")
        crop_value = None
    else:
        print(f"Warning: Unknown crop mode '{crop_mode}', defaulting to no crop")
        crop_value = None
    
    # Build output path
    if output_dir:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        crop_suffix = "nocrop" if crop_value is None else "cropped"
        output_csv = os.path.join(output_dir, f"{base_name}_{crop_suffix}_stats.csv")
    else:
        output_csv = None
    
    # Extract stats with determined crop
    df = extract_video_stats_cropped(video_path, crop_value, output_csv)
    
    return df


def main():
    """CLI interface with crop options"""
    parser = argparse.ArgumentParser(
        description='Extract video statistics with flexible cropping options',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Auto-detect black borders only (for clean videos with letterboxing)
  python script.py video.mkv --crop-mode auto
  
  # Combined detection: black borders + headswitching noise (for tapes)
  python script.py video.mkv --crop-mode combined
  
  # Headswitching detection only (no black border removal)
  python script.py video.mkv --crop-mode headswitching
  
  # Disable cropping
  python script.py video.mkv --crop-mode off
  
  # Manual crop
  python script.py video.mkv --crop-mode manual --manual-crop "1920:800:0:140"
  
  # Save output to specific directory
  python script.py video.mkv --crop-mode combined --output-dir ./stats
        '''
    )
    
    parser.add_argument('video_path', help='Path to video file')
    
    parser.add_argument('--crop-mode', 
                       choices=['auto', 'combined', 'headswitching', 'off', 'none', 'manual'],
                       default='auto',
                       help='''Crop mode:
                       auto = detect black borders only (most frequent)
                       combined = black borders + headswitching noise (two-step)
                       headswitching = headswitching noise only (no black border detection)
                       off/none = no cropping
                       manual = use --manual-crop value''')
    
    parser.add_argument('--manual-crop',
                       type=str,
                       help='Manual crop value (e.g., "1920:1080:0:0") - used with --crop-mode manual')
    
    parser.add_argument('--sample-interval',
                       type=int,
                       default=900,
                       help='Frame sampling interval for auto-detection (default: 900, use 1 for every frame)')
    
    parser.add_argument('--output-dir',
                       type=str,
                       help='Output directory for CSV file (default: current directory)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.video_path):
        print(f"Error: Video file not found: {args.video_path}")
        return 1
    
    if args.crop_mode == 'manual' and not args.manual_crop:
        print("Error: --manual-crop required when using --crop-mode manual")
        return 1
    
    if args.output_dir and not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"Created output directory: {args.output_dir}")
    
    # Process video
    df = process_video_with_options(
        args.video_path,
        output_dir=args.output_dir,
        crop_mode=args.crop_mode,
        manual_crop=args.manual_crop,
        sample_interval=args.sample_interval
    )
    
    if df is not None:
        print("\n=== Processing Complete ===")
        print(f"Frames analyzed: {len(df)}")
        print("\nDataFrame info:")
        print(df.info())
        print("\nFirst few rows:")
        print(df.head())
        return 0
    else:
        print("\nError: Processing failed")
        return 1


# For Eel interface - expose this function
def process_video_for_eel(video_path, crop_mode='auto', manual_crop=None, 
                          output_dir=None, sample_interval=900):
    """
    Wrapper function optimized for Eel interface.
    
    Args:
        video_path: Path to video file
        crop_mode: 'auto', 'combined', 'headswitching', 'off', 'none', or 'manual'
        manual_crop: Manual crop string (if crop_mode='manual')
        output_dir: Output directory for CSV
        sample_interval: Sampling interval for auto-detection
    
    Returns:
        dict with:
            - success: bool
            - message: str
            - csv_path: str (if output_dir provided)
            - stats: dict with basic statistics
            - crop_value: str or None (the crop value used)
    """
    try:
        df = process_video_with_options(
            video_path=video_path,
            output_dir=output_dir,
            crop_mode=crop_mode,
            manual_crop=manual_crop,
            sample_interval=sample_interval
        )
        
        if df is None:
            return {
                'success': False,
                'message': 'Processing failed - check console for errors',
                'csv_path': None,
                'stats': None
            }
        
        # Build output path for return
        csv_path = None
        if output_dir:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            crop_suffix = "nocrop" if crop_mode in ['off', 'none'] else "cropped"
            csv_path = os.path.join(output_dir, f"{base_name}_{crop_suffix}_stats.csv")
        
        # Basic stats for UI
        stats = {
            'total_frames': len(df),
            'duration_seconds': df['Frame Time'].max() if len(df) > 0 else 0,
            'yavg_mean': float(df['yavg'].mean()) if 'yavg' in df else None,
            'crop_applied': crop_mode not in ['off', 'none']
        }
        
        return {
            'success': True,
            'message': f'Successfully processed {len(df)} frames',
            'csv_path': csv_path,
            'stats': stats,
            'crop_value': None  # TODO: capture actual crop used
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}',
            'csv_path': None,
            'stats': None
        }


if __name__ == "__main__":
    import sys
    sys.exit(main())