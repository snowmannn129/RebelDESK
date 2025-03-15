#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script that writes output to a file.
"""

import unittest
import os

class TestWithFileOutput(unittest.TestCase):
    """Test case that writes output to a file."""
    
    def test_with_file_output(self):
        """Test method that writes output to a file."""
        with open("test_output.txt", "w") as f:
            f.write("Test is running\n")
        self.assertTrue(os.path.exists("test_output.txt"))

if __name__ == '__main__':
    with open("test_main_output.txt", "w") as f:
        f.write("Running test with file output...\n")
    unittest.main()
