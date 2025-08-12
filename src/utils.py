"""
Utility functions for file discovery and data processing
"""
import glob

def discover_files(patterns):
    """
    Discover files matching the given glob patterns
    
    Args:
        patterns: List of glob patterns
        
    Returns:
        Sorted list of unique file paths
    """
    files = []
    for pat in patterns:
        files += glob.glob(pat, recursive=True)
    return sorted(set(files))
