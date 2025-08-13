#!/usr/bin/env python3
"""
Git Commit Script - Python version for maximum compatibility
Handles quotation issues, Unicode, and special characters properly.

Usage:
    python git-commit.py "Your commit message here"
    python git-commit.py  # Interactive mode
"""

import sys
import subprocess
import shlex
from pathlib import Path


def run_git_command(command_args, capture_output=False):
    """Run a git command safely with proper error handling."""
    try:
        if capture_output:
            result = subprocess.run(
                command_args, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(
                command_args, 
                text=True, 
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode == 0, "", ""
    except Exception as e:
        print(f"Error executing git command: {e}")
        return False, "", str(e)


def get_commit_message():
    """Get commit message from command line or user input."""
    if len(sys.argv) > 1:
        # Join all arguments to handle spaces in message
        message = " ".join(sys.argv[1:])
    else:
        print("\nEnter your commit message:")
        message = input().strip()
    
    if not message:
        print("Error: Commit message cannot be empty")
        sys.exit(1)
    
    return message


def main():
    """Main commit workflow."""
    # Check if we're in a git repository
    if not Path('.git').exists():
        print("Error: Not in a git repository")
        sys.exit(1)
    
    # Get commit message
    message = get_commit_message()
    
    print(f"\nCommitting with message: {message}")
    print("-" * 50)
    
    # Stage all changes
    print("Adding all changes...")
    success, _, stderr = run_git_command(['git', 'add', '-A'])
    if not success:
        print(f"Error: Failed to stage changes - {stderr}")
        sys.exit(1)
    
    # Show status before commit
    print("\nCurrent status:")
    run_git_command(['git', 'status', '--short'])
    
    # Commit with the message
    print(f"\nCommitting...")
    success, _, stderr = run_git_command(['git', 'commit', '-m', message])
    if not success:
        print(f"Error: Commit failed - {stderr}")
        sys.exit(1)
    
    print("\nCommit successful!")
    
    # Show recent commits
    print("\nRecent commits:")
    try:
        run_git_command(['git', 'log', '--oneline', '-3'])
    except Exception as e:
        print(f"Note: Could not display recent commits - {e}")
    print()


if __name__ == "__main__":
    main()
