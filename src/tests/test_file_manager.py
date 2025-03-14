#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the FileManager class.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from src.backend.file_manager.file_manager import FileManager

class TestFileManager(unittest.TestCase):
    """Test cases for the FileManager class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test configuration
        self.config = {
            'editor': {
                'backup_files': True,
                'backup_directory': os.path.join(self.test_dir, 'backups'),
                'max_recent_files': 5
            },
            'file_types': {
                'associations': [
                    {
                        'extension': ['.py'],
                        'language': 'python'
                    },
                    {
                        'extension': ['.txt'],
                        'language': 'text'
                    }
                ]
            },
            'recent_files': []
        }
        
        # Create the file manager
        self.file_manager = FileManager(self.config)
        
        # Create some test files
        self.test_files = []
        for i in range(3):
            file_path = os.path.join(self.test_dir, f'test_file_{i}.txt')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f'Test content {i}')
            self.test_files.append(file_path)
            
        # Create a test Python file
        self.test_py_file = os.path.join(self.test_dir, 'test_file.py')
        with open(self.test_py_file, 'w', encoding='utf-8') as f:
            f.write('print("Hello, world!")')
        
    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.test_dir)
        
    def test_open_file(self):
        """Test opening a file."""
        # Test opening an existing file
        content, error = self.file_manager.open_file(self.test_files[0])
        self.assertIsNotNone(content)
        self.assertIsNone(error)
        self.assertEqual(content, 'Test content 0')
        
        # Test opening a non-existent file
        content, error = self.file_manager.open_file(os.path.join(self.test_dir, 'non_existent.txt'))
        self.assertIsNone(content)
        self.assertIsNotNone(error)
        
    def test_save_file(self):
        """Test saving a file."""
        # Test saving to a new file
        new_file = os.path.join(self.test_dir, 'new_file.txt')
        success, error = self.file_manager.save_file(new_file, 'New content')
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertTrue(os.path.exists(new_file))
        
        # Verify the content was saved correctly
        with open(new_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, 'New content')
        
        # Test saving to an existing file
        success, error = self.file_manager.save_file(self.test_files[0], 'Updated content')
        self.assertTrue(success)
        self.assertIsNone(error)
        
        # Verify the content was updated
        with open(self.test_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, 'Updated content')
        
        # Verify a backup was created
        backups = self.file_manager.get_backup_files(self.test_files[0])
        self.assertEqual(len(backups), 1)
        
    def test_add_recent_file(self):
        """Test adding a file to the recent files list."""
        # Add a file to the recent files list
        self.file_manager.add_recent_file(self.test_files[0])
        self.assertEqual(len(self.file_manager.recent_files), 1)
        self.assertEqual(self.file_manager.recent_files[0], str(Path(self.test_files[0]).resolve()))
        
        # Add the same file again (should not duplicate)
        self.file_manager.add_recent_file(self.test_files[0])
        self.assertEqual(len(self.file_manager.recent_files), 1)
        
        # Add more files to test max_recent_files
        for i in range(1, 6):
            # Create additional test files if needed
            if i >= len(self.test_files):
                file_path = os.path.join(self.test_dir, f'test_file_extra_{i}.txt')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f'Extra test content {i}')
                self.file_manager.add_recent_file(file_path)
            else:
                self.file_manager.add_recent_file(self.test_files[i % len(self.test_files)])
        
        # Now we should have 5 files in the recent files list (the max)
        self.assertEqual(len(self.file_manager.recent_files), 5)
        
    def test_get_recent_files(self):
        """Test getting the list of recent files."""
        # Add some files to the recent files list
        for file_path in self.test_files:
            self.file_manager.add_recent_file(file_path)
            
        # Get the recent files
        recent_files = self.file_manager.get_recent_files()
        self.assertEqual(len(recent_files), 3)
        
        # Delete a file and verify it's removed from recent files
        os.remove(self.test_files[0])
        recent_files = self.file_manager.get_recent_files()
        self.assertEqual(len(recent_files), 2)
        
    def test_clear_recent_files(self):
        """Test clearing the recent files list."""
        # Add some files to the recent files list
        for file_path in self.test_files:
            self.file_manager.add_recent_file(file_path)
            
        # Clear the recent files
        success = self.file_manager.clear_recent_files()
        self.assertTrue(success)
        self.assertEqual(len(self.file_manager.recent_files), 0)
        
    def test_delete_file(self):
        """Test deleting a file."""
        # Delete a file
        success, error = self.file_manager.delete_file(self.test_files[0])
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertFalse(os.path.exists(self.test_files[0]))
        
        # Verify a backup was created
        backups = self.file_manager.get_backup_files(self.test_files[0])
        self.assertEqual(len(backups), 1)
        
        # Test deleting a non-existent file
        success, error = self.file_manager.delete_file(os.path.join(self.test_dir, 'non_existent.txt'))
        self.assertFalse(success)
        self.assertIsNotNone(error)
        
    def test_rename_file(self):
        """Test renaming a file."""
        # Rename a file
        new_path = os.path.join(self.test_dir, 'renamed_file.txt')
        success, error = self.file_manager.rename_file(self.test_files[0], new_path)
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertFalse(os.path.exists(self.test_files[0]))
        self.assertTrue(os.path.exists(new_path))
        
        # Verify a backup was created
        backups = self.file_manager.get_backup_files(self.test_files[0])
        self.assertEqual(len(backups), 1)
        
        # Test renaming a non-existent file
        success, error = self.file_manager.rename_file(
            os.path.join(self.test_dir, 'non_existent.txt'),
            os.path.join(self.test_dir, 'new_name.txt')
        )
        self.assertFalse(success)
        self.assertIsNotNone(error)
        
    def test_copy_file(self):
        """Test copying a file."""
        # Copy a file
        new_path = os.path.join(self.test_dir, 'copied_file.txt')
        success, error = self.file_manager.copy_file(self.test_files[0], new_path)
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertTrue(os.path.exists(self.test_files[0]))
        self.assertTrue(os.path.exists(new_path))
        
        # Verify the content was copied correctly
        with open(new_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, 'Test content 0')
        
        # Test copying a non-existent file
        success, error = self.file_manager.copy_file(
            os.path.join(self.test_dir, 'non_existent.txt'),
            os.path.join(self.test_dir, 'new_copy.txt')
        )
        self.assertFalse(success)
        self.assertIsNotNone(error)
        
    def test_get_file_info(self):
        """Test getting file information."""
        # Get info for a file
        info = self.file_manager.get_file_info(self.test_files[0])
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], os.path.basename(self.test_files[0]))
        self.assertEqual(info['extension'], '.txt')
        self.assertFalse(info['is_dir'])
        
        # Get info for a directory
        info = self.file_manager.get_file_info(self.test_dir)
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], os.path.basename(self.test_dir))
        self.assertEqual(info['extension'], '')
        self.assertTrue(info['is_dir'])
        
        # Test getting info for a non-existent file
        info = self.file_manager.get_file_info(os.path.join(self.test_dir, 'non_existent.txt'))
        self.assertIsNone(info)
        
    def test_list_directory(self):
        """Test listing directory contents."""
        # List the test directory
        items, error = self.file_manager.list_directory(self.test_dir)
        self.assertIsNotNone(items)
        self.assertIsNone(error)
        
        # Check that all our test files and the Python file are in the list
        for file_path in self.test_files + [self.test_py_file]:
            self.assertIn(file_path, items)
            
        # Check if there's a backups directory (created by the file manager)
        backups_dir = os.path.join(self.test_dir, 'backups')
        if os.path.exists(backups_dir):
            self.assertIn(backups_dir, items)
        
        # Create a subdirectory
        subdir = os.path.join(self.test_dir, 'subdir')
        os.makedirs(subdir)
        
        # List again and verify directories are listed first
        items, error = self.file_manager.list_directory(self.test_dir)
        
        # Get all directories in the list
        directories = [item for item in items if os.path.isdir(item)]
        
        # Check that both the backups directory and the subdirectory are in the list
        self.assertIn(subdir, directories)
        backups_dir = os.path.join(self.test_dir, 'backups')
        if os.path.exists(backups_dir):
            self.assertIn(backups_dir, directories)
            
        # Check that all directories come before all files
        for dir_path in directories:
            dir_index = items.index(dir_path)
            for file_path in self.test_files + [self.test_py_file]:
                file_index = items.index(file_path)
                self.assertLess(dir_index, file_index, f"Directory {dir_path} should come before file {file_path}")
        
        # Check that all our test files and the Python file are in the list
        for file_path in self.test_files + [self.test_py_file]:
            self.assertIn(file_path, items)
            
        # Check if there's a backups directory (created by the file manager)
        backups_dir = os.path.join(self.test_dir, 'backups')
        if os.path.exists(backups_dir):
            self.assertIn(backups_dir, items)
        
        # Test listing a non-existent directory
        items, error = self.file_manager.list_directory(os.path.join(self.test_dir, 'non_existent'))
        self.assertIsNone(items)
        self.assertIsNotNone(error)
        
    def test_create_directory(self):
        """Test creating a directory."""
        # Create a new directory
        new_dir = os.path.join(self.test_dir, 'new_dir')
        success, error = self.file_manager.create_directory(new_dir)
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))
        
        # Create a nested directory
        nested_dir = os.path.join(new_dir, 'nested', 'dir')
        success, error = self.file_manager.create_directory(nested_dir)
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.isdir(nested_dir))
        
    def test_delete_directory(self):
        """Test deleting a directory."""
        # Create a directory with some files
        test_dir = os.path.join(self.test_dir, 'test_delete_dir')
        os.makedirs(test_dir)
        for i in range(2):
            file_path = os.path.join(test_dir, f'file_{i}.txt')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f'Content {i}')
                
        # Try to delete the directory without recursive flag (should fail)
        success, error = self.file_manager.delete_directory(test_dir)
        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertTrue(os.path.exists(test_dir))
        
        # Delete the directory with recursive flag
        success, error = self.file_manager.delete_directory(test_dir, recursive=True)
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertFalse(os.path.exists(test_dir))
        
        # Test deleting a non-existent directory
        success, error = self.file_manager.delete_directory(os.path.join(self.test_dir, 'non_existent'))
        self.assertFalse(success)
        self.assertIsNotNone(error)
        
    def test_get_file_type(self):
        """Test getting the file type based on extension."""
        # Test a Python file
        file_type = self.file_manager.get_file_type(self.test_py_file)
        self.assertEqual(file_type, 'python')
        
        # Test a text file
        file_type = self.file_manager.get_file_type(self.test_files[0])
        self.assertEqual(file_type, 'text')
        
        # Test a file with unknown extension
        unknown_file = os.path.join(self.test_dir, 'unknown.xyz')
        with open(unknown_file, 'w', encoding='utf-8') as f:
            f.write('Unknown content')
        file_type = self.file_manager.get_file_type(unknown_file)
        self.assertIsNone(file_type)
        
    def test_backup_and_restore(self):
        """Test backup creation and restoration."""
        # Save a file to create a backup
        self.file_manager.save_file(self.test_files[0], 'Updated content')
        
        # Get the backup files
        backups = self.file_manager.get_backup_files(self.test_files[0])
        self.assertEqual(len(backups), 1)
        
        # Modify the file again
        self.file_manager.save_file(self.test_files[0], 'Modified again')
        
        # Get the content of the backup file
        with open(backups[0], 'r', encoding='utf-8') as f:
            backup_content = f.read()
        self.assertEqual(backup_content, 'Updated content')  # Content before the second save
        
        # Restore from backup
        success, error = self.file_manager.restore_backup(backups[0], self.test_files[0])
        self.assertTrue(success)
        self.assertIsNone(error)
        
        # Verify the content was restored
        with open(self.test_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, backup_content)
        
        # Test restoring a non-existent backup
        success, error = self.file_manager.restore_backup(os.path.join(self.test_dir, 'non_existent.bak'))
        self.assertFalse(success)
        self.assertIsNotNone(error)

if __name__ == '__main__':
    unittest.main()
