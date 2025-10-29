"""
Save this as vqc/test_imports.py
Run it to see exactly which imports fail
"""

import sys
from pathlib import Path

# Add parent directory to path (same as app.py)
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print("=" * 70)
print("TESTING MEDUSIGHT IMPORTS")
print("=" * 70)

# Test 1: Can we import the package?
print("\n1. Testing package import...")
try:
    import medusight
    print("   ✓ 'import medusight' works")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Can we import processfile?
print("\n2. Testing function import...")
try:
    from medusight import processfile
    print("   ✓ 'from medusight import processfile' works")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Can we import individual modules?
print("\n3. Testing individual module imports...")
modules = [
    'video_data_extractor',
    'dataparsing',
    'audio_analysis',
    'framestatistics',
    'qcsetup',
    'overallStatistics',
    'params'
]

for mod in modules:
    try:
        exec(f"from medusight import {mod}")
        print(f"   ✓ {mod}")
    except Exception as e:
        print(f"   ✗ {mod}: {e}")

print("\n" + "=" * 70)
print("If any tests failed, those modules have import errors inside them")
print("=" * 70)