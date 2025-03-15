#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script to verify that tests are running.
"""

import unittest

class TestSimple(unittest.TestCase):
    """Simple test case."""
    
    def test_simple(self):
        """Simple test method."""
        print("Simple test is running")
        self.assertTrue(True)

if __name__ == '__main__':
    print("Running simple test...")
    unittest.main()
