"""
Tests for the plugin sandbox system.
"""

import os
import sys
import unittest
import tempfile
from unittest.mock import patch, MagicMock

from src.plugins.plugin_sandbox import (
    PluginSandbox, PluginSandboxManager, PluginPermission, ResourceLimits,
    PERMISSION_FILE_READ, PERMISSION_FILE_WRITE, PERMISSION_NETWORK,
    PERMISSION_PROCESS, PERMISSION_UI, PERMISSION_SYSTEM, PERMISSION_PLUGIN,
    PermissionDeniedError, PluginSandboxError
)

class TestPluginPermission(unittest.TestCase):
    """Tests for the PluginPermission class."""
    
    def test_initialization(self):
        """Test that the permission initializes correctly."""
        permission = PluginPermission("test", "Test permission")
        self.assertEqual(permission.name, "test")
        self.assertEqual(permission.description, "Test permission")
    
    def test_equality(self):
        """Test that permissions are equal if they have the same name."""
        permission1 = PluginPermission("test", "Test permission")
        permission2 = PluginPermission("test", "Different description")
        permission3 = PluginPermission("other", "Other permission")
        
        self.assertEqual(permission1, permission2)
        self.assertNotEqual(permission1, permission3)
        self.assertNotEqual(permission2, permission3)
    
    def test_hash(self):
        """Test that permissions can be used as dictionary keys."""
        permission1 = PluginPermission("test", "Test permission")
        permission2 = PluginPermission("test", "Different description")
        permission3 = PluginPermission("other", "Other permission")
        
        permissions = {permission1: "value1", permission3: "value3"}
        
        self.assertEqual(permissions[permission1], "value1")
        self.assertEqual(permissions[permission2], "value1")  # Same hash as permission1
        self.assertEqual(permissions[permission3], "value3")

class TestResourceLimits(unittest.TestCase):
    """Tests for the ResourceLimits class."""
    
    def test_initialization(self):
        """Test that the resource limits initialize correctly."""
        limits = ResourceLimits()
        self.assertEqual(limits.max_memory_mb, 100)
        self.assertEqual(limits.max_cpu_time_sec, 10)
        self.assertEqual(limits.max_file_handles, 10)
        self.assertEqual(limits.max_network_connections, 5)
    
    def test_custom_initialization(self):
        """Test that the resource limits initialize correctly with custom values."""
        limits = ResourceLimits(
            max_memory_mb=200,
            max_cpu_time_sec=20,
            max_file_handles=20,
            max_network_connections=10
        )
        self.assertEqual(limits.max_memory_mb, 200)
        self.assertEqual(limits.max_cpu_time_sec, 20)
        self.assertEqual(limits.max_file_handles, 20)
        self.assertEqual(limits.max_network_connections, 10)

class TestPluginSandbox(unittest.TestCase):
    """Tests for the PluginSandbox class."""
    
    def setUp(self):
        """Set up the test."""
        self.sandbox = PluginSandbox("test_plugin")
    
    def test_initialization(self):
        """Test that the sandbox initializes correctly."""
        self.assertEqual(self.sandbox.plugin_id, "test_plugin")
        self.assertEqual(len(self.sandbox.permissions), 0)
        self.assertIsInstance(self.sandbox.resource_limits, ResourceLimits)
        self.assertIn("builtins", self.sandbox.allowed_modules)
        self.assertIn("plugins.test_plugin", self.sandbox.allowed_modules)
    
    def test_has_permission(self):
        """Test that has_permission returns the correct value."""
        self.assertFalse(self.sandbox.has_permission(PERMISSION_FILE_READ))
        
        self.sandbox.permissions.add(PERMISSION_FILE_READ)
        self.assertTrue(self.sandbox.has_permission(PERMISSION_FILE_READ))
    
    def test_check_permission(self):
        """Test that check_permission raises an exception if the permission is not granted."""
        with self.assertRaises(PermissionDeniedError):
            self.sandbox.check_permission(PERMISSION_FILE_READ)
        
        self.sandbox.permissions.add(PERMISSION_FILE_READ)
        self.sandbox.check_permission(PERMISSION_FILE_READ)  # Should not raise an exception
    
    def test_create_restricted_builtins(self):
        """Test that _create_restricted_builtins returns a restricted version of builtins."""
        restricted_builtins = self.sandbox._create_restricted_builtins()
        
        # Check that dangerous functions are removed
        self.assertNotIn("exec", restricted_builtins)
        self.assertNotIn("eval", restricted_builtins)
        self.assertNotIn("compile", restricted_builtins)
        self.assertNotIn("__import__", restricted_builtins)
        
        # Check that safe functions are still present
        self.assertIn("print", restricted_builtins)
        self.assertIn("len", restricted_builtins)
        self.assertIn("str", restricted_builtins)
        
        # Check that open is replaced with a restricted version
        self.assertIn("open", restricted_builtins)
        self.assertNotEqual(restricted_builtins["open"], open)
    
    def test_restricted_open(self):
        """Test that _restricted_open checks permissions and tracks file handles."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test")
            temp_path = temp_file.name
        
        try:
            # Test that opening a file for reading requires the FILE_READ permission
            with self.assertRaises(PermissionDeniedError):
                self.sandbox._restricted_open(temp_path, "r")
            
            # Grant the FILE_READ permission
            self.sandbox.permissions.add(PERMISSION_FILE_READ)
            
            # Test that opening a file for reading works with the FILE_READ permission
            file_obj = self.sandbox._restricted_open(temp_path, "r")
            self.assertEqual(file_obj.read(), "test")
            file_obj.close()
            
            # Test that opening a file for writing requires the FILE_WRITE permission
            with self.assertRaises(PermissionDeniedError):
                self.sandbox._restricted_open(temp_path, "w")
            
            # Grant the FILE_WRITE permission
            self.sandbox.permissions.add(PERMISSION_FILE_WRITE)
            
            # Test that opening a file for writing works with the FILE_WRITE permission
            file_obj = self.sandbox._restricted_open(temp_path, "w")
            file_obj.write("new test")
            file_obj.close()
            
            # Verify that the file was written to
            with open(temp_path, "r") as f:
                self.assertEqual(f.read(), "new test")
            
            # Test that the file handle is tracked
            self.assertEqual(len(self.sandbox.open_file_handles), 0)
            file_obj = self.sandbox._restricted_open(temp_path, "r")
            self.assertEqual(len(self.sandbox.open_file_handles), 1)
            file_obj.close()
            self.assertEqual(len(self.sandbox.open_file_handles), 0)
            
            # Test that the file handle limit is enforced
            self.sandbox.resource_limits.max_file_handles = 1
            file_obj1 = self.sandbox._restricted_open(temp_path, "r")
            with self.assertRaises(PluginSandboxError):
                file_obj2 = self.sandbox._restricted_open(temp_path, "r")
            file_obj1.close()
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_restricted_import(self):
        """Test that _restricted_import checks if the module is allowed."""
        # Test that importing a disallowed module raises an exception
        with self.assertRaises(PermissionDeniedError):
            self.sandbox._restricted_import("os")
        
        # Add os to the allowed modules
        self.sandbox.allowed_modules.add("os")
        
        # Test that importing an allowed module works
        module = self.sandbox._restricted_import("os")
        self.assertEqual(module.__name__, "os")
    
    def test_create_sandbox_globals(self):
        """Test that _create_sandbox_globals returns a sandboxed globals dictionary."""
        sandbox_globals = self.sandbox._create_sandbox_globals()
        
        # Check that the globals dictionary has the expected keys
        self.assertIn("__builtins__", sandbox_globals)
        self.assertIn("__name__", sandbox_globals)
        self.assertIn("__file__", sandbox_globals)
        self.assertIn("__package__", sandbox_globals)
        self.assertIn("__import__", sandbox_globals)
        self.assertIn("__sandbox__", sandbox_globals)
        
        # Check that the values are correct
        self.assertEqual(sandbox_globals["__name__"], "plugins.test_plugin")
        self.assertEqual(sandbox_globals["__file__"], None)
        self.assertEqual(sandbox_globals["__package__"], "plugins")
        self.assertEqual(sandbox_globals["__import__"], self.sandbox._restricted_import)
        self.assertEqual(sandbox_globals["__sandbox__"], self.sandbox)

class TestPluginSandboxManager(unittest.TestCase):
    """Tests for the PluginSandboxManager class."""
    
    def setUp(self):
        """Set up the test."""
        self.manager = PluginSandboxManager()
    
    def test_initialization(self):
        """Test that the manager initializes correctly."""
        self.assertEqual(len(self.manager.sandboxes), 0)
        self.assertEqual(len(self.manager.plugin_permissions), 0)
        self.assertEqual(len(self.manager.plugin_resource_limits), 0)
        self.assertEqual(len(self.manager.plugin_allowed_modules), 0)
    
    def test_register_plugin(self):
        """Test that register_plugin registers a plugin correctly."""
        self.manager.register_plugin("test_plugin")
        
        self.assertIn("test_plugin", self.manager.plugin_permissions)
        self.assertIn("test_plugin", self.manager.plugin_resource_limits)
        self.assertIn("test_plugin", self.manager.plugin_allowed_modules)
        
        self.assertEqual(len(self.manager.plugin_permissions["test_plugin"]), 0)
        self.assertIsInstance(self.manager.plugin_resource_limits["test_plugin"], ResourceLimits)
        self.assertEqual(len(self.manager.plugin_allowed_modules["test_plugin"]), 0)
    
    def test_register_plugin_with_permissions(self):
        """Test that register_plugin registers a plugin with permissions correctly."""
        permissions = {PERMISSION_FILE_READ, PERMISSION_FILE_WRITE}
        self.manager.register_plugin("test_plugin", permissions)
        
        self.assertEqual(self.manager.plugin_permissions["test_plugin"], permissions)
    
    def test_register_plugin_with_resource_limits(self):
        """Test that register_plugin registers a plugin with resource limits correctly."""
        resource_limits = ResourceLimits(
            max_memory_mb=200,
            max_cpu_time_sec=20,
            max_file_handles=20,
            max_network_connections=10
        )
        self.manager.register_plugin("test_plugin", resource_limits=resource_limits)
        
        self.assertEqual(self.manager.plugin_resource_limits["test_plugin"], resource_limits)
    
    def test_register_plugin_with_allowed_modules(self):
        """Test that register_plugin registers a plugin with allowed modules correctly."""
        allowed_modules = {"os", "sys", "math"}
        self.manager.register_plugin("test_plugin", allowed_modules=allowed_modules)
        
        self.assertEqual(self.manager.plugin_allowed_modules["test_plugin"], allowed_modules)
    
    def test_create_sandbox(self):
        """Test that create_sandbox creates a sandbox correctly."""
        self.manager.register_plugin("test_plugin")
        sandbox = self.manager.create_sandbox("test_plugin")
        
        self.assertIsInstance(sandbox, PluginSandbox)
        self.assertEqual(sandbox.plugin_id, "test_plugin")
        self.assertEqual(sandbox.permissions, self.manager.plugin_permissions["test_plugin"])
        self.assertEqual(sandbox.resource_limits, self.manager.plugin_resource_limits["test_plugin"])
        self.assertEqual(sandbox.allowed_modules, self.manager.plugin_allowed_modules["test_plugin"])
        
        self.assertIn("test_plugin", self.manager.sandboxes)
        self.assertEqual(self.manager.sandboxes["test_plugin"], sandbox)
    
    def test_create_sandbox_unregistered_plugin(self):
        """Test that create_sandbox raises an exception for an unregistered plugin."""
        with self.assertRaises(PluginSandboxError):
            self.manager.create_sandbox("unregistered_plugin")
    
    def test_grant_permission(self):
        """Test that grant_permission grants a permission correctly."""
        self.manager.register_plugin("test_plugin")
        
        self.assertNotIn(PERMISSION_FILE_READ, self.manager.plugin_permissions["test_plugin"])
        
        self.manager.grant_permission("test_plugin", PERMISSION_FILE_READ)
        
        self.assertIn(PERMISSION_FILE_READ, self.manager.plugin_permissions["test_plugin"])
    
    def test_grant_permission_with_sandbox(self):
        """Test that grant_permission updates the sandbox permissions."""
        self.manager.register_plugin("test_plugin")
        sandbox = self.manager.create_sandbox("test_plugin")
        
        self.assertNotIn(PERMISSION_FILE_READ, sandbox.permissions)
        
        self.manager.grant_permission("test_plugin", PERMISSION_FILE_READ)
        
        self.assertIn(PERMISSION_FILE_READ, sandbox.permissions)
    
    def test_grant_permission_unregistered_plugin(self):
        """Test that grant_permission raises an exception for an unregistered plugin."""
        with self.assertRaises(PluginSandboxError):
            self.manager.grant_permission("unregistered_plugin", PERMISSION_FILE_READ)
    
    def test_revoke_permission(self):
        """Test that revoke_permission revokes a permission correctly."""
        self.manager.register_plugin("test_plugin")
        self.manager.grant_permission("test_plugin", PERMISSION_FILE_READ)
        
        self.assertIn(PERMISSION_FILE_READ, self.manager.plugin_permissions["test_plugin"])
        
        self.manager.revoke_permission("test_plugin", PERMISSION_FILE_READ)
        
        self.assertNotIn(PERMISSION_FILE_READ, self.manager.plugin_permissions["test_plugin"])
    
    def test_revoke_permission_with_sandbox(self):
        """Test that revoke_permission updates the sandbox permissions."""
        self.manager.register_plugin("test_plugin")
        sandbox = self.manager.create_sandbox("test_plugin")
        self.manager.grant_permission("test_plugin", PERMISSION_FILE_READ)
        
        self.assertIn(PERMISSION_FILE_READ, sandbox.permissions)
        
        self.manager.revoke_permission("test_plugin", PERMISSION_FILE_READ)
        
        self.assertNotIn(PERMISSION_FILE_READ, sandbox.permissions)
    
    def test_revoke_permission_unregistered_plugin(self):
        """Test that revoke_permission raises an exception for an unregistered plugin."""
        with self.assertRaises(PluginSandboxError):
            self.manager.revoke_permission("unregistered_plugin", PERMISSION_FILE_READ)
    
    def test_set_resource_limits(self):
        """Test that set_resource_limits sets resource limits correctly."""
        self.manager.register_plugin("test_plugin")
        
        resource_limits = ResourceLimits(
            max_memory_mb=200,
            max_cpu_time_sec=20,
            max_file_handles=20,
            max_network_connections=10
        )
        
        self.manager.set_resource_limits("test_plugin", resource_limits)
        
        self.assertEqual(self.manager.plugin_resource_limits["test_plugin"], resource_limits)
    
    def test_set_resource_limits_with_sandbox(self):
        """Test that set_resource_limits updates the sandbox resource limits."""
        self.manager.register_plugin("test_plugin")
        sandbox = self.manager.create_sandbox("test_plugin")
        
        resource_limits = ResourceLimits(
            max_memory_mb=200,
            max_cpu_time_sec=20,
            max_file_handles=20,
            max_network_connections=10
        )
        
        self.manager.set_resource_limits("test_plugin", resource_limits)
        
        self.assertEqual(sandbox.resource_limits, resource_limits)
    
    def test_set_resource_limits_unregistered_plugin(self):
        """Test that set_resource_limits raises an exception for an unregistered plugin."""
        with self.assertRaises(PluginSandboxError):
            self.manager.set_resource_limits("unregistered_plugin", ResourceLimits())
    
    def test_add_allowed_module(self):
        """Test that add_allowed_module adds a module correctly."""
        self.manager.register_plugin("test_plugin")
        
        self.assertNotIn("os", self.manager.plugin_allowed_modules["test_plugin"])
        
        self.manager.add_allowed_module("test_plugin", "os")
        
        self.assertIn("os", self.manager.plugin_allowed_modules["test_plugin"])
    
    def test_add_allowed_module_with_sandbox(self):
        """Test that add_allowed_module updates the sandbox allowed modules."""
        self.manager.register_plugin("test_plugin")
        sandbox = self.manager.create_sandbox("test_plugin")
        
        self.assertNotIn("os", sandbox.allowed_modules)
        
        self.manager.add_allowed_module("test_plugin", "os")
        
        self.assertIn("os", sandbox.allowed_modules)
    
    def test_add_allowed_module_unregistered_plugin(self):
        """Test that add_allowed_module raises an exception for an unregistered plugin."""
        with self.assertRaises(PluginSandboxError):
            self.manager.add_allowed_module("unregistered_plugin", "os")
    
    def test_remove_allowed_module(self):
        """Test that remove_allowed_module removes a module correctly."""
        self.manager.register_plugin("test_plugin")
        self.manager.add_allowed_module("test_plugin", "os")
        
        self.assertIn("os", self.manager.plugin_allowed_modules["test_plugin"])
        
        self.manager.remove_allowed_module("test_plugin", "os")
        
        self.assertNotIn("os", self.manager.plugin_allowed_modules["test_plugin"])
    
    def test_remove_allowed_module_with_sandbox(self):
        """Test that remove_allowed_module updates the sandbox allowed modules."""
        self.manager.register_plugin("test_plugin")
        sandbox = self.manager.create_sandbox("test_plugin")
        self.manager.add_allowed_module("test_plugin", "os")
        
        self.assertIn("os", sandbox.allowed_modules)
        
        self.manager.remove_allowed_module("test_plugin", "os")
        
        self.assertNotIn("os", sandbox.allowed_modules)
    
    def test_remove_allowed_module_unregistered_plugin(self):
        """Test that remove_allowed_module raises an exception for an unregistered plugin."""
        with self.assertRaises(PluginSandboxError):
            self.manager.remove_allowed_module("unregistered_plugin", "os")

if __name__ == "__main__":
    unittest.main()
