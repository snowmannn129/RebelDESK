#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Manager for RebelDESK.

This module handles file operations such as opening, saving, and managing recent files.
"""

import os
import logging
import shutil
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class FileManager:
    """Manages file operations for the application."""
    
    def __init__(self, config=None):
        """
        Initialize the FileManager.
        
        Args:
            config (dict, optional): Application configuration.
        """
        self.config = config or {}
        self.recent_files = self.config.get('recent_files', [])
        self.backup_enabled = self.config.get('editor', {}).get('backup_files', True)
        self.backup_dir = Path(self.config.get('editor', {}).get('backup_directory', '.rebeldesk/backups'))
        self.max_recent_files = self.config.get('editor', {}).get('max_recent_files', 10)
        
        # Create backup directory if it doesn't exist and backups are enabled
        if self.backup_enabled:
            os.makedirs(self.backup_dir, exist_ok=True)
    
    def open_file(self, file_path):
        """
        Open a file and return its contents.
        
        Args:
            file_path (str): Path to the file to open.
            
        Returns:
            tuple: (content, error_message)
                content (str): The file content if successful, None otherwise.
                error_message (str): Error message if unsuccessful, None otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add to recent files
            self.add_recent_file(file_path)
            
            logger.info(f"Opened file: {file_path}")
            return content, None
            
        except UnicodeDecodeError:
            # Try with different encodings
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    logger.info(f"Opened file with {encoding} encoding: {file_path}")
                    return content, None
                except UnicodeDecodeError:
                    continue
            
            error_msg = f"Failed to decode file: {file_path}. The file may be binary or use an unsupported encoding."
            logger.error(error_msg)
            return None, error_msg
            
        except Exception as e:
            error_msg = f"Error opening file {file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None, error_msg
    
    def save_file(self, file_path, content):
        """
        Save content to a file.
        
        Args:
            file_path (str): Path to save the file to.
            content (str): Content to save.
            
        Returns:
            tuple: (success, error_message)
                success (bool): True if successful, False otherwise.
                error_message (str): Error message if unsuccessful, None otherwise.
        """
        try:
            # Create backup if enabled and file exists
            if self.backup_enabled and os.path.exists(file_path):
                success, _ = self._create_backup(file_path)
                if not success:
                    logger.warning(f"Failed to create backup for {file_path}")
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Save the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Add to recent files
            self.add_recent_file(file_path)
            
            logger.info(f"Saved file: {file_path}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error saving file {file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def _create_backup(self, file_path):
        """
        Create a backup of a file.
        
        Args:
            file_path (str): Path to the file to backup.
            
        Returns:
            tuple: (success, backup_path)
                success (bool): True if successful, False otherwise.
                backup_path (str): Path to the backup file if successful, None otherwise.
        """
        try:
            # Create backup filename with timestamp
            file_name = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_name}.{timestamp}.bak"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Copy the file
            shutil.copy2(file_path, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            return True, backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup for {file_path}: {str(e)}", exc_info=True)
            return False, None
    
    def add_recent_file(self, file_path):
        """
        Add a file to the recent files list.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Convert to absolute path
            abs_path = str(Path(file_path).resolve())
            
            # Remove if already in list
            if abs_path in self.recent_files:
                self.recent_files.remove(abs_path)
            
            # Add to beginning of list
            self.recent_files.insert(0, abs_path)
            
            # Limit list size
            self.recent_files = self.recent_files[:self.max_recent_files]
            
            # Update config
            if self.config is not None:
                self.config['recent_files'] = self.recent_files
            
            logger.info(f"Added to recent files: {abs_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding recent file: {str(e)}", exc_info=True)
            return False
    
    def get_recent_files(self):
        """
        Get the list of recent files.
        
        Returns:
            list: List of recent file paths.
        """
        # Filter out files that no longer exist
        existing_files = [f for f in self.recent_files if os.path.exists(f)]
        
        # Update the list if files were removed
        if len(existing_files) != len(self.recent_files):
            self.recent_files = existing_files
            
            # Update config
            if self.config is not None:
                self.config['recent_files'] = self.recent_files
        
        return self.recent_files
    
    def clear_recent_files(self):
        """
        Clear the recent files list.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.recent_files = []
            
            # Update config
            if self.config is not None:
                self.config['recent_files'] = []
            
            logger.info("Cleared recent files list")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing recent files: {str(e)}", exc_info=True)
            return False
    
    def delete_file(self, file_path):
        """
        Delete a file.
        
        Args:
            file_path (str): Path to the file to delete.
            
        Returns:
            tuple: (success, error_message)
                success (bool): True if successful, False otherwise.
                error_message (str): Error message if unsuccessful, None otherwise.
        """
        try:
            # Create backup if enabled
            if self.backup_enabled:
                success, _ = self._create_backup(file_path)
                if not success:
                    logger.warning(f"Failed to create backup for {file_path}")
            
            # Delete the file
            os.remove(file_path)
            
            # Remove from recent files
            abs_path = str(Path(file_path).resolve())
            if abs_path in self.recent_files:
                self.recent_files.remove(abs_path)
                
                # Update config
                if self.config is not None:
                    self.config['recent_files'] = self.recent_files
            
            logger.info(f"Deleted file: {file_path}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting file {file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def rename_file(self, old_path, new_path):
        """
        Rename a file.
        
        Args:
            old_path (str): Current path of the file.
            new_path (str): New path for the file.
            
        Returns:
            tuple: (success, error_message)
                success (bool): True if successful, False otherwise.
                error_message (str): Error message if unsuccessful, None otherwise.
        """
        try:
            # Create backup if enabled
            if self.backup_enabled:
                success, _ = self._create_backup(old_path)
                if not success:
                    logger.warning(f"Failed to create backup for {old_path}")
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(new_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Rename the file
            os.rename(old_path, new_path)
            
            # Update recent files
            abs_old_path = str(Path(old_path).resolve())
            if abs_old_path in self.recent_files:
                self.recent_files.remove(abs_old_path)
            
            self.add_recent_file(new_path)
            
            logger.info(f"Renamed file: {old_path} -> {new_path}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error renaming file {old_path} to {new_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def copy_file(self, source_path, dest_path):
        """
        Copy a file.
        
        Args:
            source_path (str): Path to the source file.
            dest_path (str): Path to the destination file.
            
        Returns:
            tuple: (success, error_message)
                success (bool): True if successful, False otherwise.
                error_message (str): Error message if unsuccessful, None otherwise.
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(dest_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            # Add to recent files
            self.add_recent_file(dest_path)
            
            logger.info(f"Copied file: {source_path} -> {dest_path}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error copying file {source_path} to {dest_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def get_file_info(self, file_path):
        """
        Get information about a file.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            dict: File information or None if an error occurred.
        """
        try:
            path = Path(file_path)
            stat = path.stat()
            
            return {
                'name': path.name,
                'path': str(path),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'is_dir': path.is_dir(),
                'extension': path.suffix.lower() if path.suffix else '',
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}", exc_info=True)
            return None
    
    def list_directory(self, directory_path):
        """
        List the contents of a directory.
        
        Args:
            directory_path (str): Path to the directory.
            
        Returns:
            tuple: (items, error_message)
                items (list): List of file and directory paths if successful, None otherwise.
                error_message (str): Error message if unsuccessful, None otherwise.
        """
        try:
            items = []
            
            # Get all items in the directory
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                items.append(item_path)
            
            # Sort items (directories first, then files)
            items.sort(key=lambda x: (not os.path.isdir(x), x.lower()))
            
            logger.info(f"Listed directory: {directory_path}")
            return items, None
            
        except Exception as e:
            error_msg = f"Error listing directory {directory_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None, error_msg
    
    def create_directory(self, directory_path):
        """
        Create a directory.
        
        Args:
            directory_path (str): Path to the directory to create.
            
        Returns:
            tuple: (success, error_message)
                success (bool): True if successful, False otherwise.
                error_message (str): Error message if unsuccessful, None otherwise.
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            
            logger.info(f"Created directory: {directory_path}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error creating directory {directory_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def delete_directory(self, directory_path, recursive=False):
        """
        Delete a directory.
        
        Args:
            directory_path (str): Path to the directory to delete.
            recursive (bool): If True, delete the directory and its contents recursively.
            
        Returns:
            tuple: (success, error_message)
                success (bool): True if successful, False otherwise.
                error_message (str): Error message if unsuccessful, None otherwise.
        """
        try:
            if recursive:
                shutil.rmtree(directory_path)
            else:
                os.rmdir(directory_path)
            
            logger.info(f"Deleted directory: {directory_path}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting directory {directory_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def get_file_type(self, file_path):
        """
        Get the file type based on extension.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            str: File type or None if not recognized.
        """
        extension = Path(file_path).suffix.lower()
        
        # Get file type associations from config
        associations = self.config.get('file_types', {}).get('associations', [])
        
        for assoc in associations:
            if extension in assoc.get('extension', []):
                return assoc.get('language')
        
        # Default to None if not recognized
        return None
    
    def get_backup_files(self, file_path=None):
        """
        Get a list of backup files.
        
        Args:
            file_path (str, optional): If provided, only get backups for this file.
            
        Returns:
            list: List of backup file paths.
        """
        if not self.backup_enabled or not os.path.exists(self.backup_dir):
            return []
        
        try:
            backups = []
            
            for backup_file in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, backup_file)
                
                # Skip if not a file
                if not os.path.isfile(backup_path):
                    continue
                
                # Skip if not a backup file
                if not backup_file.endswith('.bak'):
                    continue
                
                # If file_path is provided, only include backups for this file
                if file_path:
                    file_name = os.path.basename(file_path)
                    if not backup_file.startswith(file_name + '.'):
                        continue
                
                backups.append(backup_path)
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Error getting backup files: {str(e)}", exc_info=True)
            return []
    
    def restore_backup(self, backup_path, target_path=None):
        """
        Restore a file from backup.
        
        Args:
            backup_path (str): Path to the backup file.
            target_path (str, optional): Path to restore to. If None, extracts from backup name.
            
        Returns:
            tuple: (success, error_message)
                success (bool): True if successful, False otherwise.
                error_message (str): Error message if unsuccessful, None otherwise.
        """
        try:
            if not os.path.exists(backup_path):
                return False, f"Backup file not found: {backup_path}"
            
            # If target_path is not provided, extract from backup name
            if not target_path:
                backup_name = os.path.basename(backup_path)
                # Remove timestamp and .bak extension
                original_name = backup_name.split('.', 1)[0]
                target_path = os.path.join(os.path.dirname(backup_path), original_name)
            
            # Read the content of the backup file
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            
            # Save the content to the target path
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            
            logger.info(f"Restored backup: {backup_path} -> {target_path}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error restoring backup {backup_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
