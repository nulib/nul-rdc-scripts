#!/usr/bin/env python3
"""
audio_analysis.py — Audio Quality Control Tool

Analyzes audio/video files for loudness, silence, and dynamic range,
then generates a detailed text report with normalization recommendations.

Supports single files and batch processing of entire directories.

Usage:
    python audio_analysis.py file.mp3 --output report.txt
    python audio_analysis.py *.wav --standard streaming
    python audio_analysis.py /path/to/folder/ --batch --output reports/
    python audio_analysis.py file.wav --target-lufs -16 --output report.txt

Standards:
    broadcast : EBU R128 / ATSC A/85       (-23 LUFS, -1 dBTP)
    streaming : Spotify / Apple / YouTube   (-14 LUFS, -1 dBTP)
    film      : SMPTE Digital Cinema        (-24 LUFS, -2 dBTP)

Supported input formats: mp3, wav, flac, aac, ogg, m4a, aiff, opus,
                         mp4, mkv, mov, avi, mxf, and most other
                         formats supported by ffmpeg.
"""

import subprocess
import json
import re
import sys
import os
import glob
import datetime
import argparse


# ---------------------------------------------------------------------------
# Supported file extensions
# ---------------------------------------------------------------------------

AUDIO_EXTENSIONS = {
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.aiff', '.aif',
    '.opus', '.wma', '.alac', '.ape', '.wv', '.mka',
}

VIDEO_EXTENSIONS = {
    '.mp4', '.mkv', '.mov', '.avi', '.mxf', '.ts', '.m2ts', '.mts',
    '.wmv', '.webm', '.flv', '.ogv', '.3gp',
}

SUPPORTED_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS


# ---------------------------------------------------------------------------
# Audio quality standards
# ---------------------------------------------------------------------------

AUDIO_STANDARDS = {
    'broadcast': {
        'name': 'EBU R128 / ATSC A/85',
        'target_lufs': -23.0,
        'lufs_tolerance': 1.0,
        'max_true_peak': -1.0,
        'max_momentary': -18.0,
        'max_short_term': -20.0,
        'silence_threshold': -60.0,
        'very_quiet_threshold': -40.0,
        'very_loud_threshold': -10.0,
        'citations': [
            'EBU R128: Loudness normalisation and permitted maximum level of audio signals',
            'ATSC A/85: Techniques for Establishing and Maintaining Audio Loudness for Digital Television',
            'ITU-R BS.1770-4: Algorithms to measure audio programme loudness and true-peak audio level',
        ],
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
            'YouTube: Target -13 to -15 LUFS',
        ],
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
            'Dolby Digital Cinema: -24 LKFS (equivalent to LUFS)',
        ],
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def format_seconds_to_hms(seconds):
    """Format a float number of seconds as HH:MM:SS.mmm."""
    try:
        total_seconds = float(seconds)
        whole_seconds = int(total_seconds)
        milliseconds = int((total_seconds - whole_seconds) * 1000)
        td = datetime.timedelta(seconds=whole_seconds)
        return f"{str(td)}.{milliseconds:03d}"
    except Exception:
        return str(seconds)


def check_ffmpeg():
    """Return True if ffmpeg is available on PATH."""
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except FileNotFoundError:
        return False


def collect_files(inputs, batch=False):
    """
    Expand the list of inputs (files, globs, directories) into a flat
    list of file paths that have supported extensions.
    Directories are always scanned recursively, regardless of --batch.
    """
    collected = []
    for inp in inputs:
        # Directory scan — always recurse into directories
        if os.path.isdir(inp):
            for root, _, files in os.walk(inp):
                for fname in sorted(files):
                    ext = os.path.splitext(fname)[1].lower()
                    if ext in SUPPORTED_EXTENSIONS:
                        collected.append(os.path.join(root, fname))
        else:
            # Glob expansion (handles wildcards passed as strings)
            expanded = glob.glob(inp)
            if not expanded:
                expanded = [inp]  # keep as-is; ffmpeg will report the error
            for path in expanded:
                ext = os.path.splitext(path)[1].lower()
                if os.path.isfile(path) and ext in SUPPORTED_EXTENSIONS:
                    collected.append(path)
                elif os.path.isfile(path):
                    print(f"  [skip] Unsupported extension: {path}")
    return collected


# ---------------------------------------------------------------------------
# FFmpeg analysis functions
# ---------------------------------------------------------------------------

def extract_audio_loudness(file_path):
    """
    Run ffmpeg loudnorm (first-pass measurement) and return integrated
    loudness, true peak, and threshold.
    """
    cmd = [
        'ffmpeg', '-i', file_path,
        '-af', 'loudnorm=print_format=json',
        '-f', 'null', '-',
    ]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=600,
        )
        stderr = result.stderr
        json_start = stderr.rfind('{')
        json_end = stderr.rfind('}') + 1
        if json_start == -1 or json_end == 0:
            print('  [error] Could not find loudnorm JSON in ffmpeg output.')
            return None
        loudness_data = json.loads(stderr[json_start:json_end])
        return {
            'integrated_lufs': float(loudness_data.get('input_i', 0)),
            'true_peak_dbtp':  float(loudness_data.get('input_tp', 0)),
            'threshold':       float(loudness_data.get('input_thresh', 0)),
        }
    except subprocess.TimeoutExpired:
        print('  [error] Loudness analysis timed out.')
        return None
    except (json.JSONDecodeError, Exception) as exc:
        print(f'  [error] Loudness analysis failed: {exc}')
        return None


def detect_silence(file_path, noise_threshold=-60.0, min_duration=0.5):
    """
    Use ffmpeg silencedetect to find periods of silence below
    noise_threshold for at least min_duration seconds.
    """
    cmd = [
        'ffmpeg', '-i', file_path,
        '-af', f'silencedetect=noise={noise_threshold}dB:d={min_duration}',
        '-f', 'null', '-',
    ]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=600,
        )
        periods = []
        silence_start = None
        for line in result.stderr.split('\n'):
            if 'silencedetect' not in line:
                continue
            m = re.search(r'silence_start: ([\d.]+)', line)
            if m:
                silence_start = float(m.group(1))
            m_end = re.search(r'silence_end: ([\d.]+)', line)
            m_dur = re.search(r'silence_duration: ([\d.]+)', line)
            if m_end and m_dur and silence_start is not None:
                end = float(m_end.group(1))
                dur = float(m_dur.group(1))
                periods.append({
                    'start': silence_start, 'end': end, 'duration': dur,
                    'start_hms': format_seconds_to_hms(silence_start),
                    'end_hms':   format_seconds_to_hms(end),
                })
                silence_start = None
        return {
            'silence_periods':        periods,
            'silence_count':          len(periods),
            'total_silence_duration': sum(p['duration'] for p in periods),
            'threshold_db':           noise_threshold,
            'min_duration':           min_duration,
        }
    except subprocess.TimeoutExpired:
        print('  [error] Silence detection timed out.')
        return None
    except Exception as exc:
        print(f'  [error] Silence detection failed: {exc}')
        return None


def detect_quiet_sections(file_path, threshold=-40.0, min_duration=2.0):
    """
    Detect passages that are very quiet (but not completely silent).
    Re-uses silencedetect with a raised threshold.
    """
    cmd = [
        'ffmpeg', '-i', file_path,
        '-af', f'silencedetect=noise={threshold}dB:d={min_duration}',
        '-f', 'null', '-',
    ]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=600,
        )
        periods = []
        quiet_start = None
        for line in result.stderr.split('\n'):
            if 'silencedetect' not in line:
                continue
            m = re.search(r'silence_start: ([\d.]+)', line)
            if m:
                quiet_start = float(m.group(1))
            m_end = re.search(r'silence_end: ([\d.]+)', line)
            m_dur = re.search(r'silence_duration: ([\d.]+)', line)
            if m_end and m_dur and quiet_start is not None:
                end = float(m_end.group(1))
                dur = float(m_dur.group(1))
                periods.append({
                    'start': quiet_start, 'end': end, 'duration': dur,
                    'start_hms': format_seconds_to_hms(quiet_start),
                    'end_hms':   format_seconds_to_hms(end),
                })
                quiet_start = None
        return {
            'quiet_periods': periods,
            'quiet_count':   len(periods),
            'threshold_db':  threshold,
        }
    except Exception as exc:
        print(f'  [error] Quiet-section detection failed: {exc}')
        return None


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def analyze_file(file_path, standard='broadcast', custom_thresholds=None):
    """
    Run a complete loudness/silence/dynamic-range analysis on one file.
    Returns a result dict.
    """
    thresholds = AUDIO_STANDARDS.get(standard, AUDIO_STANDARDS['broadcast']).copy()
    if custom_thresholds:
        thresholds.update(custom_thresholds)

    loudness = extract_audio_loudness(file_path)
    if not loudness:
        return {'success': False, 'error': 'Failed to extract loudness metrics',
                'file_path': file_path}

    silence = detect_silence(
        file_path,
        noise_threshold=thresholds['silence_threshold'],
        min_duration=0.5,
    )
    quiet = detect_quiet_sections(
        file_path,
        threshold=thresholds['very_quiet_threshold'],
        min_duration=2.0,
    )

    # Normalization offset
    offset = thresholds['target_lufs'] - loudness['integrated_lufs']
    normalization = {
        'current_lufs':      loudness['integrated_lufs'],
        'target_lufs':       thresholds['target_lufs'],
        'gain_offset_db':    offset,
        'tolerance':         thresholds['lufs_tolerance'],
        'needs_normalization': abs(offset) > thresholds['lufs_tolerance'],
    }

    lufs_ok    = abs(offset) <= thresholds['lufs_tolerance']
    peak_ok    = loudness['true_peak_dbtp'] <= thresholds['max_true_peak']
    silence_ok = (silence['silence_count'] == 0) if silence else True
    quiet_ok   = (quiet['quiet_count'] == 0)     if quiet   else True

    recommendations = []

    if not lufs_ok:
        sev = 'CRITICAL' if abs(offset) > 3.0 else 'WARNING'
        direction = 'Increase' if offset > 0 else 'Decrease'
        recommendations.append({
            'severity': sev,
            'message':  f'Audio is too {"quiet" if offset > 0 else "loud"}: '
                        f'{direction} gain by {abs(offset):.2f} dB',
            'category': 'loudness',
        })

    if not peak_ok:
        over = loudness['true_peak_dbtp'] - thresholds['max_true_peak']
        sev = 'CRITICAL' if over > 2.0 else 'WARNING'
        recommendations.append({
            'severity': sev,
            'message':  f'True peak exceeds limit by {over:.2f} dB '
                        f'(max: {thresholds["max_true_peak"]} dBTP)',
            'category': 'peak',
        })

    if not silence_ok and silence:
        recommendations.append({
            'severity': 'WARNING',
            'message':  f'{silence["silence_count"]} silence period(s) detected '
                        f'(total: {silence["total_silence_duration"]:.2f}s) '
                        f'— possible audio dropout(s)',
            'category': 'silence',
        })

    if not quiet_ok and quiet:
        recommendations.append({
            'severity': 'INFO',
            'message':  f'{quiet["quiet_count"]} quiet passage(s) detected '
                        f'(below {quiet["threshold_db"]} dB) — natural dynamic range',
            'category': 'quiet',
        })

    if lufs_ok and peak_ok and silence_ok and quiet_ok:
        recommendations.append({
            'severity': 'PASS',
            'message':  f'Audio meets {thresholds["name"]} standards',
            'category': 'overall',
        })

    # Build the access copy ffmpeg command.
    # Convention: preservation master lives at  [project]/p/<stem>p.wav
    #             access copy should go to       [project]/a/<stem>.wav
    # Uses pathlib throughout for cross-platform compatibility (Mac & Windows).
    from pathlib import Path
    abs_path = Path(file_path).resolve()
    src_stem = abs_path.stem
    src_ext  = abs_path.suffix

    # Strip trailing 'p' from stem for access filename (e.g. abc123p -> abc123)
    access_stem     = src_stem[:-1] if src_stem.endswith('p') else src_stem
    access_filename = access_stem + src_ext

    # Walk up the path looking for a directory component named exactly 'p'
    # and replace it with 'a'.
    found_p = False
    p_parts = list(abs_path.parts)  # includes drive on Windows, e.g. ['C:\\', 'proj', 'p', 'file.wav']
    for i in range(len(p_parts) - 2, 0, -1):   # skip drive/root and filename
        if p_parts[i] == 'p':
            p_parts[i]  = 'a'
            p_parts[-1] = access_filename
            access_path = Path(*p_parts)
            found_p = True
            break
    if not found_p:
        access_path = abs_path.parent / access_filename

    access_dir         = access_path.parent
    access_dir_missing = not access_dir.is_dir()

    ffmpeg_cmd = None
    ffmpeg_warning = None
    if normalization['needs_normalization']:
        ffmpeg_cmd = (
            f'ffmpeg -i "{abs_path}" '
            f'-af loudnorm=I={thresholds["target_lufs"]}'
            f':TP={thresholds["max_true_peak"]}:linear=true '
            f'"{access_path}"'
        )
        if access_dir_missing:
            ffmpeg_warning = (
                f'Access directory does not exist: {access_dir}\n'
                f'         Create it before running the normalization command.'
            )

    return {
        'success':          True,
        'file_path':        file_path,
        'standard':         thresholds,
        'loudness_metrics': loudness,
        'normalization':    normalization,
        'silence_detection': silence,
        'quiet_detection':   quiet,
        'compliance': {
            'lufs_compliant':    lufs_ok,
            'peak_compliant':    peak_ok,
            'silence_compliant': silence_ok,
            'quiet_compliant':   quiet_ok,
            'overall_pass':      lufs_ok and peak_ok and silence_ok,
        },
        'recommendations': recommendations,
        'ffmpeg_command':  ffmpeg_cmd,
        'ffmpeg_warning':  ffmpeg_warning,
        'access_path':     access_path,
        'access_dir_missing': access_dir_missing,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(result):
    """Return the full text report as a string."""
    if not result['success']:
        return (
            f"AUDIO ANALYSIS FAILED\n"
            f"File:  {result.get('file_path', 'unknown')}\n"
            f"Error: {result.get('error', 'unknown error')}\n"
        )

    std   = result['standard']
    lm    = result['loudness_metrics']
    norm  = result['normalization']
    comp  = result['compliance']
    sil   = result.get('silence_detection')
    quiet = result.get('quiet_detection')
    recs  = result['recommendations']
    fname = os.path.basename(result['file_path'])
    W = 70

    def hr(): return '=' * W + '\n'

    lines = []
    lines.append(hr())
    lines.append('AUDIO QUALITY CONTROL REPORT\n')
    lines.append(hr())
    lines.append(f'File:     {fname}\n')
    lines.append(f'Standard: {std["name"]}\n')
    lines.append(f'Status:   {"MEETS STANDARDS ✓" if comp["overall_pass"] else "NORMALIZATION RECOMMENDED ⚙"}\n')
    lines.append(f'Date:     {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    lines.append('\n')
    lines.append('NOTE: This analysis is of the source file.\n')
    lines.append('      Normalization recommendations are for access copies only.\n')
    lines.append('\n')

    lines.append(hr())
    lines.append('LOUDNESS METRICS\n')
    lines.append(hr())
    lines.append(f'Integrated Loudness:   {lm["integrated_lufs"]:>8.2f} LUFS\n')
    lines.append(f'Target Loudness:       {norm["target_lufs"]:>8.2f} LUFS\n')
    lines.append(f'Tolerance:             {norm["tolerance"]:>8.2f} LUFS\n')
    lines.append(f'Deviation:             {norm["gain_offset_db"]:>+8.2f} dB\n')
    lines.append('\n')
    lines.append(f'True Peak:             {lm["true_peak_dbtp"]:>8.2f} dBTP\n')
    lines.append(f'Maximum Allowed:       {std["max_true_peak"]:>8.2f} dBTP\n')
    lines.append('\n')

    lines.append(hr())
    lines.append('COMPLIANCE CHECKS\n')
    lines.append(hr())
    lines.append(f'LUFS Compliance:       {"✓ PASS" if comp["lufs_compliant"] else "✗ FAIL"}\n')
    lines.append(f'True Peak Compliance:  {"✓ PASS" if comp["peak_compliant"] else "✗ FAIL"}\n')
    lines.append(f'Silence Check:         {"✓ PASS" if comp["silence_compliant"] else "✗ FAIL"}\n')
    lines.append(f'Quiet Sections:        {"✓ PASS" if comp["quiet_compliant"] else "ℹ INFO"}\n')
    lines.append('\n')

    # Silence
    if sil:
        lines.append(hr())
        lines.append('SILENCE DETECTION\n')
        lines.append(hr())
        lines.append(f'Threshold:             {sil["threshold_db"]} dB\n')
        lines.append(f'Minimum Duration:      {sil["min_duration"]} s\n')
        lines.append(f'Periods Found:         {sil["silence_count"]}\n')
        if sil['silence_count'] > 0:
            lines.append(f'Total Duration:        {sil["total_silence_duration"]:.2f} s\n')
            lines.append('\nSilence Periods:\n')
            for i, p in enumerate(sil['silence_periods'], 1):
                lines.append(f'  {i:3d}. {p["start_hms"]} → {p["end_hms"]}  '
                             f'({p["duration"]:.2f}s)\n')
        else:
            lines.append('No silence periods detected.\n')
        lines.append('\n')

    # Quiet sections
    if quiet and quiet['quiet_count'] > 0:
        lines.append(hr())
        lines.append('DYNAMIC RANGE — QUIET PASSAGES\n')
        lines.append(hr())
        lines.append(f'Threshold:             {quiet["threshold_db"]} dB\n')
        lines.append(f'Passages Found:        {quiet["quiet_count"]}\n')
        lines.append('\nThese are natural quiet passages. Linear normalization\n')
        lines.append('preserves these dynamics in the access copy.\n\n')
        lines.append('Quiet Passages:\n')
        for i, p in enumerate(quiet['quiet_periods'], 1):
            lines.append(f'  {i:3d}. {p["start_hms"]} → {p["end_hms"]}  '
                         f'({p["duration"]:.2f}s)\n')
        lines.append('\n')

    # Recommendations
    lines.append(hr())
    lines.append('RECOMMENDATIONS\n')
    lines.append(hr())

    critical = [r for r in recs if r['severity'] == 'CRITICAL']
    warnings = [r for r in recs if r['severity'] == 'WARNING']
    info     = [r for r in recs if r['severity'] == 'INFO']
    passes   = [r for r in recs if r['severity'] == 'PASS']

    if critical:
        lines.append('CRITICAL:\n')
        for r in critical:
            lines.append(f'  ⚠  {r["message"]}\n')
        lines.append('\n')
    if warnings:
        lines.append('WARNINGS:\n')
        for r in warnings:
            lines.append(f'  ⚠  {r["message"]}\n')
        lines.append('\n')
    if info:
        lines.append('INFORMATIONAL:\n')
        for r in info:
            lines.append(f'  ℹ  {r["message"]}\n')
        lines.append('\n')
    if passes:
        for r in passes:
            lines.append(f'✓  {r["message"]}\n')
        lines.append('\n')

    # Normalization command
    if result.get('ffmpeg_command'):
        lines.append(hr())
        lines.append('NORMALIZATION COMMAND (access copy only — do NOT apply to source)\n')
        lines.append(hr())
        if result.get('access_dir_missing'):
            lines.append(f'⚠  WARNING: Access directory does not exist:\n')
            lines.append(f'           {os.path.dirname(result["access_path"])}\n')
            lines.append(f'           Create it before running the command below.\n\n')
        lines.append(f'{result["ffmpeg_command"]}\n')
        lines.append('\n')
        lines.append(f'This adjusts overall volume by {abs(norm["gain_offset_db"]):.2f} dB '
                     f'while preserving dynamic range.\n')
        lines.append(f'Output: {result["access_path"]}\n\n')

    # Citations
    lines.append(hr())
    lines.append('STANDARDS & CITATIONS\n')
    lines.append(hr())
    for c in std['citations']:
        lines.append(f'• {c}\n')
    lines.append('\n' + hr())

    return ''.join(lines)


def write_report(result, output_path):
    """Write the report for a single result to output_path."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(generate_report(result))
    return output_path


def print_summary(result):
    """Print a one-screen summary to the terminal."""
    fname = os.path.basename(result.get('file_path', ''))
    if not result['success']:
        print(f'  ✗ FAILED  {fname}  — {result.get("error")}')
        return

    comp = result['compliance']
    lm   = result['loudness_metrics']
    norm = result['normalization']
    std  = result['standard']

    status = '✓ PASS' if comp['overall_pass'] else '⚙ NORM'
    print(f'\n  {status}  {fname}')
    print(f'         LUFS: {lm["integrated_lufs"]:>7.2f}  (target {norm["target_lufs"]:.0f}, '
          f'deviation {norm["gain_offset_db"]:+.2f} dB)')
    print(f'         Peak: {lm["true_peak_dbtp"]:>7.2f} dBTP  (max {std["max_true_peak"]:.0f})')

    sil = result.get('silence_detection')
    if sil and sil['silence_count']:
        print(f'      Silence: {sil["silence_count"]} period(s)  '
              f'({sil["total_silence_duration"]:.1f}s total)')

    for r in result.get('recommendations', []):
        icon = {'CRITICAL': '⚠ ', 'WARNING': '⚠ ', 'INFO': 'ℹ ', 'PASS': '✓ '}.get(r['severity'], '  ')
        print(f'         {icon} {r["message"]}')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description='Audio Quality Control — loudness, silence & normalization analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        'inputs', nargs='+', metavar='FILE_OR_DIR',
        help='Audio/video file(s), glob pattern(s), or directory (with --batch)',
    )
    parser.add_argument(
        '--standard', choices=['broadcast', 'streaming', 'film'],
        default='broadcast',
        help='Loudness standard to apply (default: broadcast)',
    )
    parser.add_argument(
        '--target-lufs', type=float, metavar='LUFS',
        help='Override target integrated loudness (e.g. -16)',
    )
    parser.add_argument(
        '--max-true-peak', type=float, metavar='dBTP',
        help='Override maximum true peak level (e.g. -1)',
    )
    parser.add_argument(
        '--output', '-o', metavar='PATH',
        help=(
            'Optional. For a single file: path to .txt report. '
            'For multiple files: directory for reports. '
            'Defaults to <filename>_report.txt saved beside each source file.'
        ),
    )
    parser.add_argument(
        '--batch', action='store_true',
        help='Deprecated — directories are always scanned recursively now',
    )
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Suppress per-file ffmpeg progress; only print summaries',
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not check_ffmpeg():
        sys.exit(
            'ERROR: ffmpeg not found. Install it and ensure it is on your PATH.\n'
            '  macOS:   brew install ffmpeg\n'
            '  Ubuntu:  sudo apt install ffmpeg\n'
            '  Windows: https://ffmpeg.org/download.html\n'
        )

    # Collect files
    files = collect_files(args.inputs, batch=args.batch)
    if not files:
        sys.exit('ERROR: No supported audio/video files found in the provided inputs.')

    # Build custom threshold overrides
    custom = {}
    if args.target_lufs is not None:
        custom['target_lufs'] = args.target_lufs
    if args.max_true_peak is not None:
        custom['max_true_peak'] = args.max_true_peak

    single = len(files) == 1

    # Determine output path strategy
    if args.output:
        if single:
            out_dir  = None
            out_file = args.output if args.output.endswith('.txt') else args.output + '.txt'
        else:
            out_dir  = args.output
            out_file = None
    else:
        out_dir  = None
        out_file = None

    print(f'\nAudio Quality Control — {len(files)} file(s) — standard: {args.standard}')
    print('=' * 60)

    results = []
    for i, fpath in enumerate(files, 1):
        print(f'\n[{i}/{len(files)}] {os.path.basename(fpath)}')
        if args.quiet:
            # Redirect ffmpeg chatter by temporarily swapping stdout/stderr
            # (functions already suppress most; this hides the rest)
            pass

        result = analyze_file(fpath, standard=args.standard,
                              custom_thresholds=custom if custom else None)
        results.append(result)
        print_summary(result)

        # Determine this file's report path
        if out_file and single:
            rpath = out_file
        elif out_dir:
            stem  = os.path.splitext(os.path.basename(fpath))[0]
            rpath = os.path.join(out_dir, f'{stem}_report.txt')
        else:
            stem  = os.path.splitext(fpath)[0]
            rpath = stem + '_report.txt'

        write_report(result, rpath)
        print(f'         Report: {rpath}')

    # Batch summary
    if not single:
        passed  = sum(1 for r in results if r.get('success') and r['compliance']['overall_pass'])
        failed  = sum(1 for r in results if not r.get('success'))
        norm_needed = len(results) - passed - failed
        print(f'\n{"=" * 60}')
        print(f'BATCH SUMMARY — {len(results)} file(s)')
        print(f'  ✓ Pass:             {passed}')
        print(f'  ⚙ Needs attention:  {norm_needed}')
        if failed:
            print(f'  ✗ Failed:           {failed}')
        print(f'{"=" * 60}\n')


if __name__ == '__main__':
    main()