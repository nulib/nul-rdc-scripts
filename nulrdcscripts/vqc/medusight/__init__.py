# medusight/__init__.py
"""Medusight - Video Quality Control Analysis Tool"""

__version__ = "1.0.0"

# Export main functions
from .medusight import processfile, process_file

__all__ = ['processfile', 'process_file']