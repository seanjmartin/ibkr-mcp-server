#!/usr/bin/env python3
"""
Windows-compatible Unicode Character Finder and Replacer
Finds and replaces Unicode characters in Python files with ASCII alternatives.
"""

import os
import re
import glob
from typing import Dict, List, Tuple

# Unicode to ASCII mapping
UNICODE_REPLACEMENTS = {
    # Arrows  
    '\u2192': ' -> ',  # →
    '\u2190': ' <- ',  # ←
    '\u2191': ' ^ ',   # ↑
    '\u2193': ' v ',   # ↓
    
    # Check marks and symbols
    '\u2705': '[OK]',     # ✅
    '\u2713': '[OK]',     # ✓
    '\u2714': '[OK]',     # ✔
    
    # Warning symbols
    '\u26a0': '[WARNING]',  # ⚠
    '\ufe0f': '',           # ️ variation selector - remove
    
    # Cross marks
    '\u274c': '[ERROR]',    # ❌
    '\u2717': '[ERROR]',    # ✗
    '\u2716': '[ERROR]',    # ✖
    
    # Information and currency symbols
    '\u2139': '[INFO]',      # ℹ️
    '\u20ac': 'EUR',         # €
    '\u00a3': 'GBP',         # £
    '\u00a5': 'JPY',         # ¥
    
    # Other symbols
    '\ud83c\udf89': '[SUCCESS]',  # 🎉
    '\ud83d\udd27': '[TOOL]',     # 🔧
    '\ud83d\udcca': '[DATA]',     # 📊
}

def find_unicode_in_file(filepath: str) -> List[Tuple[int, int, str, int]]:
    """Find Unicode characters in a file, returning line, pos, char, codepoint."""
    unicode_chars = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            for pos, char in enumerate(line):
                if ord(char) > 127:  # Non-ASCII
                    unicode_chars.append((line_num, pos, char, ord(char)))
    
    except Exception as e:
        print(f"[ERROR] Reading {filepath}: {e}")
    
    return unicode_chars

def fix_unicode_in_file(filepath: str) -> Tuple[int, int]:
    """Fix Unicode characters in a file. Returns (found_count, fixed_count)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Reading {filepath}: {e}")
        return 0, 0
    
    # Count Unicode characters before fixing
    unicode_count = len([c for c in content if ord(c) > 127])
    
    if unicode_count == 0:
        return 0, 0
    
    # Apply replacements
    original_content = content
    fixes_applied = 0
    
    for unicode_char, replacement in UNICODE_REPLACEMENTS.items():
        if unicode_char in content:
            count_before = content.count(unicode_char)
            content = content.replace(unicode_char, replacement)
            fixes_applied += count_before
    
    # Write back if changes were made
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[FIXED] {filepath}: {fixes_applied} replacements")
        except Exception as e:
            print(f"[ERROR] Writing {filepath}: {e}")
            return unicode_count, 0
    
    return unicode_count, fixes_applied

def scan_test_files(root_dir: str, fix_mode: bool = False):
    """Scan all Python test files for Unicode characters."""
    test_patterns = [
        'tests/**/*.py',
        'test_*.py'
    ]
    
    all_files = []
    for pattern in test_patterns:
        files = glob.glob(os.path.join(root_dir, pattern), recursive=True)
        all_files.extend(files)
    
    # Remove duplicates and sort
    all_files = sorted(list(set(all_files)))
    
    print(f"Scanning {len(all_files)} test files...")
    print(f"Mode: {'FIX' if fix_mode else 'FIND ONLY'}")
    print("=" * 60)
    
    total_unicode = 0
    total_fixed = 0
    problem_files = []
    
    for filepath in all_files:
        if fix_mode:
            unicode_count, fixed_count = fix_unicode_in_file(filepath)
        else:
            unicode_chars = find_unicode_in_file(filepath)
            unicode_count = len(unicode_chars)
            fixed_count = 0
            
            if unicode_count > 0:
                rel_path = os.path.relpath(filepath, root_dir)
                print(f"[FOUND] {rel_path}: {unicode_count} Unicode characters")
                
                # Show first few examples (avoid printing Unicode to console)
                for line_num, pos, char, codepoint in unicode_chars[:3]:
                    replacement = UNICODE_REPLACEMENTS.get(char, '[NO MAPPING]')
                    print(f"  Line {line_num}, Pos {pos}: U+{codepoint:04X} -> {replacement}")
                
                if len(unicode_chars) > 3:
                    print(f"  ... and {len(unicode_chars) - 3} more")
        
        if unicode_count > 0:
            total_unicode += unicode_count
            total_fixed += fixed_count
            problem_files.append((filepath, unicode_count, fixed_count))
    
    # Summary
    print("=" * 60)
    print(f"SUMMARY:")
    print(f"Files scanned: {len(all_files)}")
    print(f"Files with Unicode: {len(problem_files)}")
    print(f"Total Unicode characters: {total_unicode}")
    
    if fix_mode:
        print(f"Characters fixed: {total_fixed}")
        print(f"Characters remaining: {total_unicode - total_fixed}")
    
    return total_unicode, total_fixed

if __name__ == '__main__':
    root_dir = r"C:\Users\sean\Documents\Projects\ibkr-mcp-server"
    
    # First scan to find
    print("=== UNICODE CHARACTER SCAN ===")
    unicode_count, _ = scan_test_files(root_dir, fix_mode=False)
    
    if unicode_count > 0:
        print(f"\nFound {unicode_count} Unicode characters in test files.")
        print("\nRunning automatic fix...")
        
        # Fix them
        print("\n=== APPLYING FIXES ===")
        _, fixed_count = scan_test_files(root_dir, fix_mode=True)
        
        print(f"\nFixed {fixed_count} Unicode characters.")
        
        # Final scan to check remaining
        print("\n=== VERIFICATION SCAN ===")
        remaining_count, _ = scan_test_files(root_dir, fix_mode=False)
        
        if remaining_count == 0:
            print("\nALL UNICODE CHARACTERS FIXED! Tests should now work on Windows.")
        else:
            print(f"\n{remaining_count} Unicode characters remain (need manual review)")
    else:
        print("\nNo Unicode characters found in test files!")
