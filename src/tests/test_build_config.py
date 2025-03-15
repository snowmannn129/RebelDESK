#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the build configuration system.

This module contains tests for the build configuration manager.
"""

import os
import sys
import pytest
import tempfile
import json
from pathlib import Path

from src.backend.compiler.build_config import BuildConfigManager

class TestBuildConfigManager:
    """Tests for the BuildConfigManager class."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary configuration file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_file.write(b'{}')
            temp_path = temp_file.name
        
        yield temp_path
        
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def build_config_manager(self, temp_config_file):
        """Create a BuildConfigManager instance for testing."""
        return BuildConfigManager(temp_config_file)
    
    def test_init_creates_default_configs(self, build_config_manager):
        """Test that initialization creates default configurations."""
        languages = build_config_manager.get_languages()
        assert len(languages) > 0
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'cpp' in languages
        assert 'java' in languages
    
    def test_get_configs(self, build_config_manager):
        """Test getting configurations for a language."""
        python_configs = build_config_manager.get_configs('python')
        assert isinstance(python_configs, list)
        assert len(python_configs) > 0
        
        # Check that each configuration has the required fields
        for config in python_configs:
            assert 'name' in config
            assert 'args' in config
            assert 'description' in config
    
    def test_get_config(self, build_config_manager):
        """Test getting a specific configuration."""
        # Get a configuration that should exist
        config = build_config_manager.get_config('python', 'Default')
        assert config is not None
        assert config['name'] == 'Default'
        assert 'args' in config
        assert 'description' in config
        
        # Get a configuration that doesn't exist
        config = build_config_manager.get_config('python', 'NonExistent')
        assert config is None
    
    def test_add_config(self, build_config_manager):
        """Test adding a new configuration."""
        # Add a new configuration
        result = build_config_manager.add_config(
            'python',
            'TestConfig',
            ['-u', '-v'],
            'Test configuration'
        )
        assert result is True
        
        # Check that the configuration was added
        config = build_config_manager.get_config('python', 'TestConfig')
        assert config is not None
        assert config['name'] == 'TestConfig'
        assert config['args'] == ['-u', '-v']
        assert config['description'] == 'Test configuration'
        
        # Try to add a configuration with the same name (should fail)
        result = build_config_manager.add_config(
            'python',
            'TestConfig',
            ['-u', '-vv'],
            'Another test configuration'
        )
        assert result is False
    
    def test_update_config(self, build_config_manager):
        """Test updating an existing configuration."""
        # Add a test configuration
        build_config_manager.add_config(
            'python',
            'TestConfig',
            ['-u', '-v'],
            'Test configuration'
        )
        
        # Update the configuration
        result = build_config_manager.update_config(
            'python',
            'TestConfig',
            ['-u', '-vv'],
            'Updated test configuration'
        )
        assert result is True
        
        # Check that the configuration was updated
        config = build_config_manager.get_config('python', 'TestConfig')
        assert config is not None
        assert config['name'] == 'TestConfig'
        assert config['args'] == ['-u', '-vv']
        assert config['description'] == 'Updated test configuration'
        
        # Try to update a non-existent configuration (should fail)
        result = build_config_manager.update_config(
            'python',
            'NonExistent',
            ['-u', '-vv'],
            'Updated test configuration'
        )
        assert result is False
    
    def test_delete_config(self, build_config_manager):
        """Test deleting a configuration."""
        # Add a test configuration
        build_config_manager.add_config(
            'python',
            'TestConfig',
            ['-u', '-v'],
            'Test configuration'
        )
        
        # Delete the configuration
        result = build_config_manager.delete_config('python', 'TestConfig')
        assert result is True
        
        # Check that the configuration was deleted
        config = build_config_manager.get_config('python', 'TestConfig')
        assert config is None
        
        # Try to delete a non-existent configuration (should fail)
        result = build_config_manager.delete_config('python', 'NonExistent')
        assert result is False
    
    def test_rename_config(self, build_config_manager):
        """Test renaming a configuration."""
        # Add a test configuration
        build_config_manager.add_config(
            'python',
            'TestConfig',
            ['-u', '-v'],
            'Test configuration'
        )
        
        # Rename the configuration
        result = build_config_manager.rename_config('python', 'TestConfig', 'RenamedConfig')
        assert result is True
        
        # Check that the configuration was renamed
        config = build_config_manager.get_config('python', 'TestConfig')
        assert config is None
        
        config = build_config_manager.get_config('python', 'RenamedConfig')
        assert config is not None
        assert config['name'] == 'RenamedConfig'
        
        # Try to rename a non-existent configuration (should fail)
        result = build_config_manager.rename_config('python', 'NonExistent', 'NewName')
        assert result is False
        
        # Try to rename to a name that already exists (should fail)
        build_config_manager.add_config(
            'python',
            'ExistingConfig',
            ['-u', '-v'],
            'Existing configuration'
        )
        
        result = build_config_manager.rename_config('python', 'RenamedConfig', 'ExistingConfig')
        assert result is False
    
    def test_duplicate_config(self, build_config_manager):
        """Test duplicating a configuration."""
        # Add a test configuration
        build_config_manager.add_config(
            'python',
            'TestConfig',
            ['-u', '-v'],
            'Test configuration'
        )
        
        # Duplicate the configuration
        result = build_config_manager.duplicate_config('python', 'TestConfig', 'DuplicatedConfig')
        assert result is True
        
        # Check that the configuration was duplicated
        config = build_config_manager.get_config('python', 'TestConfig')
        assert config is not None
        
        config = build_config_manager.get_config('python', 'DuplicatedConfig')
        assert config is not None
        assert config['name'] == 'DuplicatedConfig'
        assert config['args'] == ['-u', '-v']
        assert "Copy of" in config['description']
        
        # Try to duplicate a non-existent configuration (should fail)
        result = build_config_manager.duplicate_config('python', 'NonExistent', 'NewConfig')
        assert result is False
        
        # Try to duplicate to a name that already exists (should fail)
        result = build_config_manager.duplicate_config('python', 'TestConfig', 'DuplicatedConfig')
        assert result is False
    
    def test_import_export_configs(self, build_config_manager, temp_config_file):
        """Test importing and exporting configurations."""
        # Add a test configuration
        build_config_manager.add_config(
            'python',
            'TestConfig',
            ['-u', '-v'],
            'Test configuration'
        )
        
        # Export configurations to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as export_file:
            export_path = export_file.name
        
        try:
            # Export configurations
            result = build_config_manager.export_configs(export_path)
            assert result is True
            
            # Check that the file was created and contains the configurations
            assert os.path.exists(export_path)
            
            with open(export_path, 'r') as f:
                exported_configs = json.load(f)
            
            assert 'python' in exported_configs
            assert any(config['name'] == 'TestConfig' for config in exported_configs['python'])
            
            # Create a new configuration manager with a different config file
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as new_config_file:
                new_config_path = new_config_file.name
            
            try:
                new_manager = BuildConfigManager(new_config_path)
                
                # Add a different test configuration
                new_manager.add_config(
                    'python',
                    'AnotherConfig',
                    ['-u', '-vvv'],
                    'Another test configuration'
                )
                
                # Import the exported configurations
                result = new_manager.import_configs(export_path)
                assert result is True
                
                # Check that both configurations are now available
                config = new_manager.get_config('python', 'TestConfig')
                assert config is not None
                assert config['name'] == 'TestConfig'
                
                config = new_manager.get_config('python', 'AnotherConfig')
                assert config is not None
                assert config['name'] == 'AnotherConfig'
                
            finally:
                # Clean up
                if os.path.exists(new_config_path):
                    os.unlink(new_config_path)
                
        finally:
            # Clean up
            if os.path.exists(export_path):
                os.unlink(export_path)
    
    def test_reset_to_defaults(self, build_config_manager):
        """Test resetting configurations to defaults."""
        # Add a test configuration
        build_config_manager.add_config(
            'python',
            'TestConfig',
            ['-u', '-v'],
            'Test configuration'
        )
        
        # Check that the configuration was added
        config = build_config_manager.get_config('python', 'TestConfig')
        assert config is not None
        
        # Reset to defaults
        result = build_config_manager.reset_to_defaults()
        assert result is True
        
        # Check that the custom configuration was removed
        config = build_config_manager.get_config('python', 'TestConfig')
        assert config is None
        
        # Check that default configurations are still available
        config = build_config_manager.get_config('python', 'Default')
        assert config is not None
