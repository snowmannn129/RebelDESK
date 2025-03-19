"""
Tests for the plugin manager.
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.plugins.plugin_manager import PluginManager, PluginMetadata
from src.plugins.plugin_sandbox import (
    PluginSandboxManager, PluginPermission, ResourceLimits,
    PERMISSION_FILE_READ, PERMISSION_FILE_WRITE, PERMISSION_NETWORK,
    PERMISSION_PROCESS, PERMISSION_UI, PERMISSION_SYSTEM, PERMISSION_PLUGIN
)

class TestPluginMetadata(unittest.TestCase):
    """Tests for the PluginMetadata class."""
    
    def test_initialization(self):
        """Test that the metadata initializes correctly."""
        metadata = PluginMetadata(
            plugin_id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="A test plugin",
            author="Test Author",
            dependencies=["dep1", "dep2"],
            permissions=["file_read", "file_write"],
            min_app_version="0.1.0",
            max_app_version="1.0.0",
            homepage="https://example.com",
            repository="https://github.com/example/test-plugin",
            tags=["test", "example"]
        )
        
        self.assertEqual(metadata.plugin_id, "test-plugin")
        self.assertEqual(metadata.name, "Test Plugin")
        self.assertEqual(metadata.version, "1.0.0")
        self.assertEqual(metadata.description, "A test plugin")
        self.assertEqual(metadata.author, "Test Author")
        self.assertEqual(metadata.dependencies, ["dep1", "dep2"])
        self.assertEqual(metadata.permissions, ["file_read", "file_write"])
        self.assertEqual(metadata.min_app_version, "0.1.0")
        self.assertEqual(metadata.max_app_version, "1.0.0")
        self.assertEqual(metadata.homepage, "https://example.com")
        self.assertEqual(metadata.repository, "https://github.com/example/test-plugin")
        self.assertEqual(metadata.tags, ["test", "example"])
    
    def test_from_dict(self):
        """Test that from_dict creates a metadata object correctly."""
        data = {
            "plugin_id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author",
            "dependencies": ["dep1", "dep2"],
            "permissions": ["file_read", "file_write"],
            "min_app_version": "0.1.0",
            "max_app_version": "1.0.0",
            "homepage": "https://example.com",
            "repository": "https://github.com/example/test-plugin",
            "tags": ["test", "example"]
        }
        
        metadata = PluginMetadata.from_dict(data)
        
        self.assertEqual(metadata.plugin_id, "test-plugin")
        self.assertEqual(metadata.name, "Test Plugin")
        self.assertEqual(metadata.version, "1.0.0")
        self.assertEqual(metadata.description, "A test plugin")
        self.assertEqual(metadata.author, "Test Author")
        self.assertEqual(metadata.dependencies, ["dep1", "dep2"])
        self.assertEqual(metadata.permissions, ["file_read", "file_write"])
        self.assertEqual(metadata.min_app_version, "0.1.0")
        self.assertEqual(metadata.max_app_version, "1.0.0")
        self.assertEqual(metadata.homepage, "https://example.com")
        self.assertEqual(metadata.repository, "https://github.com/example/test-plugin")
        self.assertEqual(metadata.tags, ["test", "example"])
    
    def test_from_dict_missing_required_fields(self):
        """Test that from_dict raises an exception if required fields are missing."""
        data = {
            "name": "Test Plugin",
            "version": "1.0.0"
        }
        
        with self.assertRaises(ValueError):
            PluginMetadata.from_dict(data)
    
    def test_to_dict(self):
        """Test that to_dict converts a metadata object to a dictionary correctly."""
        metadata = PluginMetadata(
            plugin_id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="A test plugin",
            author="Test Author",
            dependencies=["dep1", "dep2"],
            permissions=["file_read", "file_write"],
            min_app_version="0.1.0",
            max_app_version="1.0.0",
            homepage="https://example.com",
            repository="https://github.com/example/test-plugin",
            tags=["test", "example"]
        )
        
        data = metadata.to_dict()
        
        self.assertEqual(data["plugin_id"], "test-plugin")
        self.assertEqual(data["name"], "Test Plugin")
        self.assertEqual(data["version"], "1.0.0")
        self.assertEqual(data["description"], "A test plugin")
        self.assertEqual(data["author"], "Test Author")
        self.assertEqual(data["dependencies"], ["dep1", "dep2"])
        self.assertEqual(data["permissions"], ["file_read", "file_write"])
        self.assertEqual(data["min_app_version"], "0.1.0")
        self.assertEqual(data["max_app_version"], "1.0.0")
        self.assertEqual(data["homepage"], "https://example.com")
        self.assertEqual(data["repository"], "https://github.com/example/test-plugin")
        self.assertEqual(data["tags"], ["test", "example"])

class TestPluginManager(unittest.TestCase):
    """Tests for the PluginManager class."""
    
    def setUp(self):
        """Set up the test."""
        # Create a temporary directory for plugins
        self.plugin_dir = tempfile.mkdtemp()
        
        # Create a plugin manager
        self.manager = PluginManager()
        
        # Add the temporary directory as a plugin directory
        self.manager.add_plugin_dir(self.plugin_dir)
        
        # Create a test plugin
        self.create_test_plugin()
    
    def tearDown(self):
        """Clean up after the test."""
        # Remove the temporary directory
        shutil.rmtree(self.plugin_dir)
    
    def create_test_plugin(self):
        """Create a test plugin in the temporary directory."""
        # Create the plugin directory
        plugin_dir = os.path.join(self.plugin_dir, "test-plugin")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create the plugin.json file
        metadata = {
            "plugin_id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author",
            "dependencies": [],
            "permissions": ["file_read", "file_write"],
            "min_app_version": "0.1.0",
            "max_app_version": "1.0.0",
            "homepage": "https://example.com",
            "repository": "https://github.com/example/test-plugin",
            "tags": ["test", "example"]
        }
        
        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump(metadata, f)
        
        # Create the main.py file
        main_py = """
class TestPlugin:
    def __init__(self):
        self.name = "Test Plugin"
    
    def activate(self, app=None):
        return True
    
    def deactivate(self):
        return True
"""
        
        with open(os.path.join(plugin_dir, "main.py"), "w") as f:
            f.write(main_py)
    
    def create_dependency_plugin(self):
        """Create a dependency plugin in the temporary directory."""
        # Create the plugin directory
        plugin_dir = os.path.join(self.plugin_dir, "dep-plugin")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create the plugin.json file
        metadata = {
            "plugin_id": "dep-plugin",
            "name": "Dependency Plugin",
            "version": "1.0.0",
            "description": "A dependency plugin",
            "author": "Test Author",
            "dependencies": [],
            "permissions": ["file_read"],
            "min_app_version": "0.1.0",
            "max_app_version": "1.0.0",
            "homepage": "https://example.com",
            "repository": "https://github.com/example/dep-plugin",
            "tags": ["test", "example"]
        }
        
        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump(metadata, f)
        
        # Create the main.py file
        main_py = """
class DepPlugin:
    def __init__(self):
        self.name = "Dependency Plugin"
    
    def activate(self, app=None):
        return True
    
    def deactivate(self):
        return True
"""
        
        with open(os.path.join(plugin_dir, "main.py"), "w") as f:
            f.write(main_py)
        
        # Update the test plugin to depend on the dependency plugin
        test_plugin_dir = os.path.join(self.plugin_dir, "test-plugin")
        with open(os.path.join(test_plugin_dir, "plugin.json"), "r") as f:
            metadata = json.load(f)
        
        metadata["dependencies"] = ["dep-plugin"]
        
        with open(os.path.join(test_plugin_dir, "plugin.json"), "w") as f:
            json.dump(metadata, f)
    
    def test_initialization(self):
        """Test that the manager initializes correctly."""
        self.assertEqual(len(self.manager.plugin_dirs), 1)
        self.assertEqual(self.manager.plugin_dirs[0], self.plugin_dir)
        self.assertEqual(len(self.manager.plugins), 0)
        self.assertEqual(len(self.manager.active_plugins), 0)
        self.assertEqual(len(self.manager.plugin_metadata), 0)
        self.assertIsInstance(self.manager.sandbox_manager, PluginSandboxManager)
    
    def test_add_plugin_dir(self):
        """Test that add_plugin_dir adds a directory correctly."""
        # Create a new temporary directory
        new_dir = tempfile.mkdtemp()
        
        try:
            # Add the directory
            self.manager.add_plugin_dir(new_dir)
            
            # Check that the directory was added
            self.assertIn(new_dir, self.manager.plugin_dirs)
        finally:
            # Clean up
            shutil.rmtree(new_dir)
    
    def test_add_plugin_dir_nonexistent(self):
        """Test that add_plugin_dir handles nonexistent directories correctly."""
        # Add a nonexistent directory
        self.manager.add_plugin_dir("/nonexistent/directory")
        
        # Check that the directory was not added
        self.assertNotIn("/nonexistent/directory", self.manager.plugin_dirs)
    
    def test_discover_plugins(self):
        """Test that discover_plugins finds plugins correctly."""
        # Discover plugins
        plugins = self.manager.discover_plugins()
        
        # Check that the test plugin was found
        self.assertIn("test-plugin", plugins)
        self.assertEqual(plugins["test-plugin"].name, "Test Plugin")
        self.assertEqual(plugins["test-plugin"].version, "1.0.0")
    
    def test_get_plugin_path(self):
        """Test that _get_plugin_path returns the correct path."""
        # Get the plugin path
        path = self.manager._get_plugin_path("test-plugin")
        
        # Check that the path is correct
        self.assertEqual(path, os.path.join(self.plugin_dir, "test-plugin", "main.py"))
    
    def test_get_plugin_path_nonexistent(self):
        """Test that _get_plugin_path handles nonexistent plugins correctly."""
        # Get the plugin path
        path = self.manager._get_plugin_path("nonexistent-plugin")
        
        # Check that the path is None
        self.assertIsNone(path)
    
    def test_get_plugin_metadata_path(self):
        """Test that _get_plugin_metadata_path returns the correct path."""
        # Get the plugin metadata path
        path = self.manager._get_plugin_metadata_path("test-plugin")
        
        # Check that the path is correct
        self.assertEqual(path, os.path.join(self.plugin_dir, "test-plugin", "plugin.json"))
    
    def test_get_plugin_metadata_path_nonexistent(self):
        """Test that _get_plugin_metadata_path handles nonexistent plugins correctly."""
        # Get the plugin metadata path
        path = self.manager._get_plugin_metadata_path("nonexistent-plugin")
        
        # Check that the path is None
        self.assertIsNone(path)
    
    def test_load_plugin_metadata(self):
        """Test that _load_plugin_metadata loads metadata correctly."""
        # Load the plugin metadata
        metadata = self.manager._load_plugin_metadata("test-plugin")
        
        # Check that the metadata is correct
        self.assertEqual(metadata.plugin_id, "test-plugin")
        self.assertEqual(metadata.name, "Test Plugin")
        self.assertEqual(metadata.version, "1.0.0")
    
    def test_load_plugin_metadata_nonexistent(self):
        """Test that _load_plugin_metadata handles nonexistent plugins correctly."""
        # Load the plugin metadata
        metadata = self.manager._load_plugin_metadata("nonexistent-plugin")
        
        # Check that the metadata is None
        self.assertIsNone(metadata)
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    def test_load_plugin(self, mock_load_plugin):
        """Test that load_plugin loads a plugin correctly."""
        # Mock the sandbox manager's load_plugin method
        mock_plugin = MagicMock()
        mock_load_plugin.return_value = mock_plugin
        
        # Load the plugin
        result = self.manager.load_plugin("test-plugin")
        
        # Check that the plugin was loaded
        self.assertTrue(result)
        self.assertIn("test-plugin", self.manager.plugins)
        self.assertEqual(self.manager.plugins["test-plugin"], mock_plugin)
        self.assertIn("test-plugin", self.manager.plugin_metadata)
        self.assertEqual(self.manager.plugin_metadata["test-plugin"].name, "Test Plugin")
        
        # Check that the sandbox manager's load_plugin method was called
        mock_load_plugin.assert_called_once()
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    def test_load_plugin_with_dependencies(self, mock_load_plugin):
        """Test that load_plugin loads dependencies correctly."""
        # Create a dependency plugin
        self.create_dependency_plugin()
        
        # Mock the sandbox manager's load_plugin method
        mock_plugin = MagicMock()
        mock_load_plugin.return_value = mock_plugin
        
        # Load the plugin
        result = self.manager.load_plugin("test-plugin")
        
        # Check that the plugin and its dependency were loaded
        self.assertTrue(result)
        self.assertIn("test-plugin", self.manager.plugins)
        self.assertIn("dep-plugin", self.manager.plugins)
        
        # Check that the sandbox manager's load_plugin method was called twice
        self.assertEqual(mock_load_plugin.call_count, 2)
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    def test_load_plugin_nonexistent(self, mock_load_plugin):
        """Test that load_plugin handles nonexistent plugins correctly."""
        # Load the plugin
        result = self.manager.load_plugin("nonexistent-plugin")
        
        # Check that the plugin was not loaded
        self.assertFalse(result)
        self.assertNotIn("nonexistent-plugin", self.manager.plugins)
        
        # Check that the sandbox manager's load_plugin method was not called
        mock_load_plugin.assert_not_called()
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.activate_plugin")
    def test_activate_plugin(self, mock_activate_plugin, mock_load_plugin):
        """Test that activate_plugin activates a plugin correctly."""
        # Mock the sandbox manager's methods
        mock_plugin = MagicMock()
        mock_load_plugin.return_value = mock_plugin
        mock_activate_plugin.return_value = True
        
        # Load the plugin
        self.manager.load_plugin("test-plugin")
        
        # Activate the plugin
        result = self.manager.activate_plugin("test-plugin")
        
        # Check that the plugin was activated
        self.assertTrue(result)
        self.assertIn("test-plugin", self.manager.active_plugins)
        
        # Check that the sandbox manager's activate_plugin method was called
        mock_activate_plugin.assert_called_once_with("test-plugin", self.manager.app)
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.activate_plugin")
    def test_activate_plugin_not_loaded(self, mock_activate_plugin, mock_load_plugin):
        """Test that activate_plugin handles plugins that are not loaded correctly."""
        # Activate the plugin
        result = self.manager.activate_plugin("test-plugin")
        
        # Check that the plugin was not activated
        self.assertFalse(result)
        self.assertNotIn("test-plugin", self.manager.active_plugins)
        
        # Check that the sandbox manager's activate_plugin method was not called
        mock_activate_plugin.assert_not_called()
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.activate_plugin")
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.deactivate_plugin")
    def test_deactivate_plugin(self, mock_deactivate_plugin, mock_activate_plugin, mock_load_plugin):
        """Test that deactivate_plugin deactivates a plugin correctly."""
        # Mock the sandbox manager's methods
        mock_plugin = MagicMock()
        mock_load_plugin.return_value = mock_plugin
        mock_activate_plugin.return_value = True
        mock_deactivate_plugin.return_value = True
        
        # Load and activate the plugin
        self.manager.load_plugin("test-plugin")
        self.manager.activate_plugin("test-plugin")
        
        # Deactivate the plugin
        result = self.manager.deactivate_plugin("test-plugin")
        
        # Check that the plugin was deactivated
        self.assertTrue(result)
        self.assertNotIn("test-plugin", self.manager.active_plugins)
        
        # Check that the sandbox manager's deactivate_plugin method was called
        mock_deactivate_plugin.assert_called_once_with("test-plugin")
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.deactivate_plugin")
    def test_deactivate_plugin_not_loaded(self, mock_deactivate_plugin, mock_load_plugin):
        """Test that deactivate_plugin handles plugins that are not loaded correctly."""
        # Deactivate the plugin
        result = self.manager.deactivate_plugin("test-plugin")
        
        # Check that the plugin was not deactivated
        self.assertFalse(result)
        
        # Check that the sandbox manager's deactivate_plugin method was not called
        mock_deactivate_plugin.assert_not_called()
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.activate_plugin")
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.deactivate_plugin")
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.unload_plugin")
    def test_unload_plugin(self, mock_unload_plugin, mock_deactivate_plugin, mock_activate_plugin, mock_load_plugin):
        """Test that unload_plugin unloads a plugin correctly."""
        # Mock the sandbox manager's methods
        mock_plugin = MagicMock()
        mock_load_plugin.return_value = mock_plugin
        mock_activate_plugin.return_value = True
        mock_deactivate_plugin.return_value = True
        mock_unload_plugin.return_value = True
        
        # Load and activate the plugin
        self.manager.load_plugin("test-plugin")
        self.manager.activate_plugin("test-plugin")
        
        # Unload the plugin
        result = self.manager.unload_plugin("test-plugin")
        
        # Check that the plugin was unloaded
        self.assertTrue(result)
        self.assertNotIn("test-plugin", self.manager.plugins)
        self.assertNotIn("test-plugin", self.manager.active_plugins)
        self.assertNotIn("test-plugin", self.manager.plugin_metadata)
        
        # Check that the sandbox manager's methods were called
        mock_deactivate_plugin.assert_called_once_with("test-plugin")
        mock_unload_plugin.assert_called_once_with("test-plugin")
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.unload_plugin")
    def test_unload_plugin_not_loaded(self, mock_unload_plugin):
        """Test that unload_plugin handles plugins that are not loaded correctly."""
        # Unload the plugin
        result = self.manager.unload_plugin("test-plugin")
        
        # Check that the plugin was not unloaded
        self.assertFalse(result)
        
        # Check that the sandbox manager's unload_plugin method was not called
        mock_unload_plugin.assert_not_called()
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    def test_get_plugin_metadata(self, mock_load_plugin):
        """Test that get_plugin_metadata returns the correct metadata."""
        # Mock the sandbox manager's load_plugin method
        mock_plugin = MagicMock()
        mock_load_plugin.return_value = mock_plugin
        
        # Load the plugin
        self.manager.load_plugin("test-plugin")
        
        # Get the plugin metadata
        metadata = self.manager.get_plugin_metadata("test-plugin")
        
        # Check that the metadata is correct
        self.assertEqual(metadata.plugin_id, "test-plugin")
        self.assertEqual(metadata.name, "Test Plugin")
        self.assertEqual(metadata.version, "1.0.0")
    
    def test_get_plugin_metadata_not_loaded(self):
        """Test that get_plugin_metadata handles plugins that are not loaded correctly."""
        # Get the plugin metadata
        metadata = self.manager.get_plugin_metadata("test-plugin")
        
        # Check that the metadata is None
        self.assertIsNone(metadata)
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    def test_is_plugin_loaded(self, mock_load_plugin):
        """Test that is_plugin_loaded returns the correct value."""
        # Mock the sandbox manager's load_plugin method
        mock_plugin = MagicMock()
        mock_load_plugin.return_value = mock_plugin
        
        # Check that the plugin is not loaded
        self.assertFalse(self.manager.is_plugin_loaded("test-plugin"))
        
        # Load the plugin
        self.manager.load_plugin("test-plugin")
        
        # Check that the plugin is loaded
        self.assertTrue(self.manager.is_plugin_loaded("test-plugin"))
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.activate_plugin")
    def test_is_plugin_active(self, mock_activate_plugin, mock_load_plugin):
        """Test that is_plugin_active returns the correct value."""
        # Mock the sandbox manager's methods
        mock_plugin = MagicMock()
        mock_load_plugin.return_value = mock_plugin
        mock_activate_plugin.return_value = True
        
        # Check that the plugin is not active
        self.assertFalse(self.manager.is_plugin_active("test-plugin"))
        
        # Load and activate the plugin
        self.manager.load_plugin("test-plugin")
        self.manager.activate_plugin("test-plugin")
        
        # Check that the plugin is active
        self.assertTrue(self.manager.is_plugin_active("test-plugin"))
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    def test_get_loaded_plugins(self, mock_load_plugin):
        """Test that get_loaded_plugins returns the correct list."""
        # Mock the sandbox manager's load_plugin method
        mock_plugin = MagicMock()
        mock_load_plugin.return_value = mock_plugin
        
        # Check that the list is empty
        self.assertEqual(self.manager.get_loaded_plugins(), [])
        
        # Load the plugin
        self.manager.load_plugin("test-plugin")
        
        # Check that the list contains the plugin
        self.assertEqual(self.manager.get_loaded_plugins(), ["test-plugin"])
    
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.load_plugin")
    @patch("src.plugins.plugin_sandbox.PluginSandboxManager.activate_plugin")
    def test_get_active_plugins(self, mock_activate_plugin, mock_load_plugin):
        """Test that get_active_plugins returns the correct list."""
        # Mock the sandbox manager's methods
        mock_plugin = MagicMock()
        mock_load_plugin.return_value = mock_plugin
        mock_activate_plugin.return_value = True
        
        # Check that the list is empty
        self.assertEqual(self.manager.get_active_plugins(), [])
        
        # Load and activate the plugin
        self.manager.load_plugin("test-plugin")
        self.manager.activate_plugin("test-plugin")
        
        # Check that the list contains the plugin
        self.assertEqual(self.manager.get_active_plugins(), ["test-plugin"])

if __name__ == "__main__":
    unittest.main()
