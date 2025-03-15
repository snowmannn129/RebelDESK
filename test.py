#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for RebelDESK terminal.

This script demonstrates the terminal functionality by printing colored text
and executing some basic operations.
"""

import sys
import os
import time
import random

def print_colored(text, color_code):
    """Print colored text using ANSI escape codes."""
    print(f"\033[{color_code}m{text}\033[0m")

def main():
    """Main function."""
    print_colored("RebelDESK Terminal Test", "1;36")  # Bold Cyan
    print_colored("========================", "1;36")  # Bold Cyan
    print()
    
    # Print system information
    print_colored("System Information:", "1;33")  # Bold Yellow
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # Simulate a task with progress
    print_colored("Simulating a task with progress:", "1;33")  # Bold Yellow
    for i in range(10):
        progress = i * 10
        print(f"\rProgress: {progress}% [{'#' * (i+1)}{' ' * (9-i)}]", end="")
        time.sleep(0.5)
    print("\rProgress: 100% [##########] Complete!")
    print()
    
    # Print colored text examples
    print_colored("Colored Text Examples:", "1;33")  # Bold Yellow
    print_colored("This is \033[31mred\033[0m text.", "0")
    print_colored("This is \033[32mgreen\033[0m text.", "0")
    print_colored("This is \033[33myellow\033[0m text.", "0")
    print_colored("This is \033[34mblue\033[0m text.", "0")
    print_colored("This is \033[35mmagenta\033[0m text.", "0")
    print_colored("This is \033[36mcyan\033[0m text.", "0")
    print()
    
    # Generate some random numbers
    print_colored("Random Numbers:", "1;33")  # Bold Yellow
    for i in range(5):
        num = random.randint(1, 100)
        print(f"Random number {i+1}: {num}")
    print()
    
    # List files in the current directory
    print_colored("Files in Current Directory:", "1;33")  # Bold Yellow
    files = os.listdir(".")
    for file in files[:10]:  # Show only first 10 files
        if os.path.isdir(file):
            print_colored(f"📁 {file}/", "1;34")  # Bold Blue for directories
        else:
            print(f"📄 {file}")
    
    if len(files) > 10:
        print(f"... and {len(files) - 10} more files")
    print()
    
    print_colored("Test completed successfully!", "1;32")  # Bold Green

if __name__ == "__main__":
    main()
