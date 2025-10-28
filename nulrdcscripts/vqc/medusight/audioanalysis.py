import subprocess
import json
import re
import datetime
import os


def format_seconds_to_hms(seconds):
    """Format seconds to HH:MM:SS.mmm format."""
    try:
        total_seconds = float(seconds)
        whole_seconds = int(total_seconds)
        milliseconds = int((total_seconds - whole_seconds) * 1000)
        td = datetime.timedelta(seconds=whole_seconds)
        return f"{str(td)}.{milliseconds:03d}"
    except Exception:
        return str(seconds)


# Audio Quality Standards with Citations
AUDIO_STANDARDS = {
    'broadcast': {
        'name': 'EBU R128 / ATSC A/85',
        'target_lufs': -23.0,
        'lufs_tolerance': 0.5,
        'max_true_peak': -1.0,
        'max_momentary': -18.0,
        'max_short_term': -20.0,
        'silence_threshold': -60.0,
        'very_quiet_threshold': -40.0,
        'very_loud_threshold': -10.0,
        'citations': [
            'EBU R128: Loudness normalisation and permitted maximum level of audio signals',
            'ATSC A/85: Techniques for Establishing and Maintaining Audio Loudness for Digital Television',
            'ITU-R BS.1770-4: Algorithms to measure audio programme loudness and true-peak audio level'
        ]
    },
    'streaming': {
        'name': 'Streaming Services (Spotify, Apple Music, YouTube)',
        'target_lufs': -14.0,
        'lufs_tolerance': 1.0,
        'max_true_peak': -1.0,
        'max_momentary': -8.0,
        'max_short_term': -11.0,
        'silence_threshold': -60.0,
        'very_quiet_threshold': -35.0,
        'very_loud_threshold': -8.0,
        'citations': [
            'Spotify: Target -14 LUFS integrated loudness',
            'Apple Music: Target -16 LUFS (Sound Check)',
            'YouTube: Target -13 to -15 LUFS'
        ]
    },
    'film': {
        'name': 'Digital Cinema (SMPTE)',
        'target_lufs': -24.0,
        'lufs_tolerance': 1.0,
        'max_true_peak': -2.0,
        'max_momentary': -15.0,
        'max_short_term': -18.0,
        'silence_threshold': -70.0,
        'very_quiet_threshold': -50.0,
        'very_loud_threshold': -12.0,
        'citations': [
            'SMPTE ST 2067-3: Audio Channel Mapping and Program Loudness',
            'Dolby Digital Cinema: -24 LKFS (equivalent to LUFS)'
        ]
    }
}


def detect_silence(video_path, noise_threshold=-60.0, min_duration=0.5):
    """
    Detect periods of silence in audio.
    
    Args:
        video_path: Path to video file
        noise_threshold: dB threshold below which audio is considered silent (default: -60 dB)
        min_duration: Minimum duration in seconds to count as silence (default: 0.5)
    
    Returns:
        dict with silence detection results
    """
    print(f"Detecting silence in: {video_path}")
    print(f"Threshold: {noise_threshold} dB, Min duration: {min_duration}s")
    
    # Use silencedetect filter
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-af', f'silencedetect=noise={noise_threshold}dB:d={min_duration}',
        '-f', 'null',
        '-'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300
        )
        
        stderr = result.stderr
        
        # Parse silence start and end times
        silence_periods = []
        silence_start = None
        
        for line in stderr.split('\n'):
            if 'silencedetect' in line:
                # Look for silence_start
                start_match = re.search(r'silence_start: ([\d.]+)', line)
                if start_match:
                    silence_start = float(start_match.group(1))
                
                # Look for silence_end
                end_match = re.search(r'silence_end: ([\d.]+)', line)
                duration_match = re.search(r'silence_duration: ([\d.]+)', line)
                
                if end_match and duration_match and silence_start is not None:
                    silence_end = float(end_match.group(1))
                    duration = float(duration_match.group(1))
                    
                    silence_periods.append({
                        'start': silence_start,
                        'end': silence_end,
                        'duration': duration,
                        'start_hms': format_seconds_to_hms(silence_start),
                        'end_hms': format_seconds_to_hms(silence_end)
                    })
                    
                    silence_start = None
        
        total_silence_duration = sum(s['duration'] for s in silence_periods)
        
        print(f"Found {len(silence_periods)} silence period(s)")
        print(f"Total silence duration: {total_silence_duration:.2f}s")
        
        return {
            'silence_periods': silence_periods,
            'silence_count': len(silence_periods),
            'total_silence_duration': total_silence_duration,
            'threshold_db': noise_threshold,
            'min_duration': min_duration
        }
        
    except subprocess.TimeoutExpired:
        print("Error: Silence detection timed out")
        return None
    except Exception as e:
        print(f"Error during silence detection: {e}")
        return None


def extract_audio_loudness(video_path):
    """
    Extract audio loudness metrics using FFmpeg loudnorm filter.
    
    Measures:
    - Integrated loudness (LUFS)
    - Loudness range (LRA)
    - True peak (dBTP)
    - Threshold
    
    Args:
        video_path: Path to video file
    
    Returns:
        dict with loudness metrics, or None if extraction fails
    """
    print(f"Analyzing audio loudness for: {video_path}")
    
    # Run loudnorm in measurement mode (first pass)
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-af', 'loudnorm=print_format=json',
        '-f', 'null',
        '-'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # loudnorm outputs JSON to stderr
        stderr = result.stderr
        
        # Extract JSON from stderr (it's after the last occurrence of "Parsed_loudnorm")
        json_start = stderr.rfind('{')
        json_end = stderr.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            print("Error: Could not find loudnorm JSON output")
            return None
        
        json_str = stderr[json_start:json_end]
        loudness_data = json.loads(json_str)
        
        # Parse the values
        integrated = float(loudness_data.get('input_i', 0))
        true_peak = float(loudness_data.get('input_tp', 0))
        lra = float(loudness_data.get('input_lra', 0))
        threshold = float(loudness_data.get('input_thresh', 0))
        
        print(f"Integrated Loudness: {integrated:.2f} LUFS")
        print(f"True Peak: {true_peak:.2f} dBTP")
        print(f"Loudness Range: {lra:.2f} LU")
        
        return {
            'integrated_lufs': integrated,
            'true_peak_dbtp': true_peak,
            'loudness_range_lu': lra,
            'threshold': threshold
        }
        
    except subprocess.TimeoutExpired:
        print("Error: Audio analysis timed out")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing loudnorm JSON: {e}")
        return None
    except Exception as e:
        print(f"Error during audio analysis: {e}")
        return None


def detect_very_quiet_sections(video_path, threshold=-40.0, min_duration=2.0):
    """
    Detect sections that are very quiet (but not silent).
    These may indicate recording issues or weak audio levels.
    
    Args:
        video_path: Path to video file
        threshold: dB threshold for "very quiet" (default: -40 dB)
        min_duration: Minimum duration in seconds (default: 2.0)
    
    Returns:
        dict with very quiet sections
    """
    print(f"Detecting very quiet sections (threshold: {threshold} dB)")
    
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-af', f'silencedetect=noise={threshold}dB:d={min_duration}',
        '-f', 'null',
        '-'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300
        )
        
        stderr = result.stderr
        quiet_periods = []
        quiet_start = None
        
        for line in stderr.split('\n'):
            if 'silencedetect' in line:
                start_match = re.search(r'silence_start: ([\d.]+)', line)
                if start_match:
                    quiet_start = float(start_match.group(1))
                
                end_match = re.search(r'silence_end: ([\d.]+)', line)
                duration_match = re.search(r'silence_duration: ([\d.]+)', line)
                
                if end_match and duration_match and quiet_start is not None:
                    quiet_end = float(end_match.group(1))
                    duration = float(duration_match.group(1))
                    
                    quiet_periods.append({
                        'start': quiet_start,
                        'end': quiet_end,
                        'duration': duration,
                        'start_hms': format_seconds_to_hms(quiet_start),
                        'end_hms': format_seconds_to_hms(quiet_end)
                    })
                    
                    quiet_start = None
        
        print(f"Found {len(quiet_periods)} very quiet section(s)")
        
        return {
            'quiet_periods': quiet_periods,
            'quiet_count': len(quiet_periods),
            'threshold_db': threshold
        }
        
    except Exception as e:
        print(f"Error detecting quiet sections: {e}")
        return None


def calculate_normalization_offset(current_lufs, target_lufs=-23.0, tolerance=0.5):
    """
    Calculate the gain adjustment needed to reach target loudness.
    
    Args:
        current_lufs: Current integrated loudness in LUFS
        target_lufs: Target loudness in LUFS (default: -23.0 for broadcast)
        tolerance: Acceptable deviation from target (default: 0.5 LUFS)
    
    Returns:
        dict with normalization recommendations
    """
    offset = target_lufs - current_lufs
    
    return {
        'current_lufs': current_lufs,
        'target_lufs': target_lufs,
        'gain_offset_db': offset,
        'tolerance': tolerance,
        'needs_normalization': abs(offset) > tolerance
    }


def analyze_audio_quality(video_path, standard='broadcast', custom_thresholds=None):
    """
    Complete audio quality analysis workflow with configurable standards.
    
    Args:
        video_path: Path to video file
        standard: Predefined standard ('broadcast', 'streaming', 'film')
        custom_thresholds: Optional dict to override standard thresholds
    
    Returns:
        dict with analysis results and recommendations
    """
    # Get standard thresholds
    if standard in AUDIO_STANDARDS:
        thresholds = AUDIO_STANDARDS[standard].copy()
    else:
        print(f"Unknown standard '{standard}', defaulting to 'broadcast'")
        thresholds = AUDIO_STANDARDS['broadcast'].copy()
    
    # Override with custom thresholds if provided
    if custom_thresholds:
        thresholds.update(custom_thresholds)
    
    print(f"\n{'='*60}")
    print(f"Using standard: {thresholds['name']}")
    print(f"{'='*60}\n")
    
    # Extract loudness metrics
    loudness = extract_audio_loudness(video_path)
    
    if not loudness:
        return {
            'success': False,
            'error': 'Failed to extract audio loudness metrics'
        }
    
    # Detect silence
    silence_result = detect_silence(
        video_path, 
        noise_threshold=thresholds['silence_threshold'],
        min_duration=0.5
    )
    
    # Detect very quiet sections
    quiet_result = detect_very_quiet_sections(
        video_path,
        threshold=thresholds['very_quiet_threshold'],
        min_duration=2.0
    )
    
    # Calculate normalization
    normalization = calculate_normalization_offset(
        loudness['integrated_lufs'], 
        thresholds['target_lufs'],
        thresholds['lufs_tolerance']
    )
    
    # Check compliance
    lufs_compliant = abs(normalization['gain_offset_db']) <= thresholds['lufs_tolerance']
    peak_compliant = loudness['true_peak_dbtp'] <= thresholds['max_true_peak']
    silence_compliant = silence_result['silence_count'] == 0 if silence_result else True
    quiet_compliant = quiet_result['quiet_count'] == 0 if quiet_result else True
    
    # Generate recommendations with severity levels
    recommendations = []
    
    # LUFS check
    if not lufs_compliant:
        severity = "CRITICAL" if abs(normalization['gain_offset_db']) > 3.0 else "WARNING"
        if normalization['gain_offset_db'] > 0:
            recommendations.append({
                'severity': severity,
                'message': f"Audio is too quiet: Increase gain by {normalization['gain_offset_db']:.2f} dB",
                'category': 'loudness'
            })
        else:
            recommendations.append({
                'severity': severity,
                'message': f"Audio is too loud: Decrease gain by {abs(normalization['gain_offset_db']):.2f} dB",
                'category': 'loudness'
            })
    
    # True peak check
    if not peak_compliant:
        over_peak = loudness['true_peak_dbtp'] - thresholds['max_true_peak']
        severity = "CRITICAL" if over_peak > 2.0 else "WARNING"
        recommendations.append({
            'severity': severity,
            'message': f"True peak exceeds limit by {over_peak:.2f} dB (max: {thresholds['max_true_peak']} dBTP)",
            'category': 'peak'
        })
    
    # Silence check
    if not silence_compliant and silence_result:
        recommendations.append({
            'severity': 'WARNING',
            'message': f"{silence_result['silence_count']} silence period(s) detected "
                      f"(total: {silence_result['total_silence_duration']:.2f}s) - Possible audio dropouts",
            'category': 'silence'
        })
    
    # Very quiet sections check
    if not quiet_compliant and quiet_result:
        recommendations.append({
            'severity': 'INFO',
            'message': f"{quiet_result['quiet_count']} very quiet section(s) detected "
                      f"(below {quiet_result['threshold_db']} dB)",
            'category': 'quiet'
        })
    
    # All clear
    if lufs_compliant and peak_compliant and silence_compliant and quiet_compliant:
        recommendations.append({
            'severity': 'PASS',
            'message': f"Audio meets {thresholds['name']} standards",
            'category': 'overall'
        })
    
    # FFmpeg normalization command
    if normalization['needs_normalization']:
        ffmpeg_cmd = (
            f"ffmpeg -i input.mkv "
            f"-af loudnorm=I={thresholds['target_lufs']}:TP={thresholds['max_true_peak']}:LRA=7 "
            f"-c:v copy output.mkv"
        )
    else:
        ffmpeg_cmd = None
    
    return {
        'success': True,
        'standard': thresholds,
        'loudness_metrics': loudness,
        'normalization': normalization,
        'silence_detection': silence_result,
        'quiet_detection': quiet_result,
        'compliance': {
            'lufs_compliant': lufs_compliant,
            'peak_compliant': peak_compliant,
            'silence_compliant': silence_compliant,
            'quiet_compliant': quiet_compliant,
            'overall_pass': lufs_compliant and peak_compliant and silence_compliant
        },
        'recommendations': recommendations,
        'ffmpeg_command': ffmpeg_cmd
    }


def generate_audio_report(analysis_result, output_path):
    """
    Generate a detailed text report for audio analysis.
    
    Args:
        analysis_result: Result dict from analyze_audio_quality()
        output_path: Where to save the report (.txt file)
    """
    if not analysis_result['success']:
        report = f"Audio Analysis Failed\nError: {analysis_result.get('error', 'Unknown error')}\n"
    else:
        standard = analysis_result['standard']
        loudness = analysis_result['loudness_metrics']
        norm = analysis_result['normalization']
        compliance = analysis_result['compliance']
        silence = analysis_result.get('silence_detection')
        quiet = analysis_result.get('quiet_detection')
        recommendations = analysis_result['recommendations']
        
        # Build report
        report = f"""{'='*70}
AUDIO QUALITY CONTROL REPORT
{'='*70}

Standard: {standard['name']}
Status: {'PASS ✓' if compliance['overall_pass'] else 'FAIL ✗'}
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*70}
LOUDNESS METRICS
{'='*70}

Integrated Loudness:     {loudness['integrated_lufs']:>8.2f} LUFS
Target Loudness:         {norm['target_lufs']:>8.2f} LUFS
Tolerance:               {norm['tolerance']:>8.2f} LUFS
Deviation:               {norm['gain_offset_db']:>+8.2f} dB

True Peak:               {loudness['true_peak_dbtp']:>8.2f} dBTP
Maximum Allowed:         {standard['max_true_peak']:>8.2f} dBTP

Loudness Range (LRA):    {loudness['loudness_range_lu']:>8.2f} LU

{'='*70}
COMPLIANCE CHECKS
{'='*70}

LUFS Compliance:         {'✓ PASS' if compliance['lufs_compliant'] else '✗ FAIL'}
True Peak Compliance:    {'✓ PASS' if compliance['peak_compliant'] else '✗ FAIL'}
Silence Check:           {'✓ PASS' if compliance['silence_compliant'] else '✗ FAIL'}
Quiet Sections Check:    {'✓ PASS' if compliance['quiet_compliant'] else '✗ INFO'}

"""
        
        # Add silence detection results
        if silence:
            report += f"""{'='*70}
SILENCE DETECTION
{'='*70}

Threshold:               {silence['threshold_db']} dB
Minimum Duration:        {silence['min_duration']} seconds
Periods Found:           {silence['silence_count']}
"""
            if silence['silence_count'] > 0:
                report += f"Total Duration:          {silence['total_silence_duration']:.2f} seconds\n\n"
                report += "Silence Periods:\n"
                for i, period in enumerate(silence['silence_periods'], 1):
                    report += f"  {i:2d}. {period['start_hms']} → {period['end_hms']} "
                    report += f"(duration: {period['duration']:.2f}s)\n"
            else:
                report += "\nNo silence periods detected.\n"
            report += "\n"
        
        # Add very quiet sections
        if quiet and quiet['quiet_count'] > 0:
            report += f"""{'='*70}
VERY QUIET SECTIONS
{'='*70}

Threshold:               {quiet['threshold_db']} dB
Sections Found:          {quiet['quiet_count']}

Quiet Sections:
"""
            for i, period in enumerate(quiet['quiet_periods'], 1):
                report += f"  {i:2d}. {period['start_hms']} → {period['end_hms']} "
                report += f"(duration: {period['duration']:.2f}s)\n"
            report += "\n"
        
        # Add recommendations
        report += f"""{'='*70}
RECOMMENDATIONS
{'='*70}

"""
        
        # Group by severity
        critical = [r for r in recommendations if r['severity'] == 'CRITICAL']
        warnings = [r for r in recommendations if r['severity'] == 'WARNING']
        info = [r for r in recommendations if r['severity'] == 'INFO']
        passes = [r for r in recommendations if r['severity'] == 'PASS']
        
        if critical:
            report += "CRITICAL ISSUES:\n"
            for rec in critical:
                report += f"  ⚠ {rec['message']}\n"
            report += "\n"
        
        if warnings:
            report += "WARNINGS:\n"
            for rec in warnings:
                report += f"  ⚠ {rec['message']}\n"
            report += "\n"
        
        if info:
            report += "INFORMATIONAL:\n"
            for rec in info:
                report += f"  ℹ {rec['message']}\n"
            report += "\n"
        
        if passes:
            for rec in passes:
                report += f"✓ {rec['message']}\n"
            report += "\n"
        
        # Add normalization command
        if analysis_result.get('ffmpeg_command'):
            report += f"""{'='*70}
NORMALIZATION COMMAND
{'='*70}

{analysis_result['ffmpeg_command']}

"""
        
        # Add citations
        report += f"""{'='*70}
STANDARDS & CITATIONS
{'='*70}

"""
        for citation in standard['citations']:
            report += f"• {citation}\n"
        
        report += f"\n{'='*70}\n"
    
    # Write report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n{'='*60}")
    print(f"Audio report written to: {output_path}")
    print(f"{'='*60}\n")


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze audio loudness with silence detection and generate normalization recommendations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Standards:
  broadcast : EBU R128 / ATSC A/85 (-23 LUFS, -1 dBTP)
  streaming : Spotify, Apple Music, YouTube (-14 LUFS, -1 dBTP)
  film      : SMPTE Digital Cinema (-24 LUFS, -2 dBTP)

Examples:
  # Broadcast standard analysis
  python audio_analysis.py video.mkv --standard broadcast --output report.txt
  
  # Streaming platform analysis
  python audio_analysis.py video.mkv --standard streaming --output report.txt
  
  # Custom thresholds
  python audio_analysis.py video.mkv --target-lufs -16 --output report.txt
        """
    )
    
    parser.add_argument('video_path', help='Path to video file')
    parser.add_argument('--standard', choices=['broadcast', 'streaming', 'film'],
                       default='broadcast',
                       help='Audio standard to use (default: broadcast)')
    parser.add_argument('--target-lufs', type=float,
                       help='Override target integrated loudness in LUFS')
    parser.add_argument('--max-true-peak', type=float,
                       help='Override maximum true peak in dBTP')
    parser.add_argument('--output', type=str, required=True,
                       help='Output path for report (.txt file)')
    
    args = parser.parse_args()
    
    # Ensure output has .txt extension
    if not args.output.endswith('.txt'):
        args.output += '.txt'
    
    # Build custom thresholds if provided
    custom_thresholds = {}
    if args.target_lufs is not None:
        custom_thresholds['target_lufs'] = args.target_lufs
    if args.max_true_peak is not None:
        custom_thresholds['max_true_peak'] = args.max_true_peak
    
    # Run analysis
    result = analyze_audio_quality(
        args.video_path,
        standard=args.standard,
        custom_thresholds=custom_thresholds if custom_thresholds else None
    )
    
    # Generate report
    if result['success']:
        generate_audio_report(result, args.output)
        
        # Print summary to console
        print("\n" + "="*60)
        print("AUDIO ANALYSIS SUMMARY")
        print("="*60)
        
        compliance = result['compliance']
        print(f"Overall Status: {'PASS ✓' if compliance['overall_pass'] else 'FAIL ✗'}")
        print(f"\nLUFS: {result['loudness_metrics']['integrated_lufs']:.2f} LUFS "
              f"(target: {result['normalization']['target_lufs']:.2f})")
        print(f"True Peak: {result['loudness_metrics']['true_peak_dbtp']:.2f} dBTP "
              f"(max: {result['standard']['max_true_peak']:.2f})")
        
        if result['silence_detection']:
            print(f"Silence Periods: {result['silence_detection']['silence_count']}")
        
        print("\nRecommendations:")
        for rec in result['recommendations']:
            severity_icon = {'CRITICAL': '⚠', 'WARNING': '⚠', 'INFO': 'ℹ', 'PASS': '✓'}
            icon = severity_icon.get(rec['severity'], '•')
            print(f"  {icon} {rec['message']}")
        
        print(f"\nDetailed report: {args.output}")
        print("="*60)
    else:
        print(f"Analysis failed: {result.get('error')}")