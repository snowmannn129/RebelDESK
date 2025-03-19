"""
Plugin sandboxing system for RebelDESK.

This module provides a sandboxing system for plugins to enhance security
by restricting plugin access to system resources and isolating plugins
from each other and the main application.
"""

import os
import sys
import importlib
import importlib.util
import inspect
import logging
import threading
import multiprocessing
import time
import traceback
from typing import Dict, Any, Optional, List, Set, Callable, Tuple, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class PermissionDeniedError(Exception):
    """Exception raised when a plugin attempts to perform an action without permission."""
    pass

class PluginSandboxError(Exception):
    """Exception raised when there's an error in the plugin sandbox."""
    pass

class PluginPermission:
    """
    Represents a permission that can be granted to a plugin.
    
    Permissions control what actions a plugin is allowed to perform,
    such as accessing the file system, network, or system resources.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize a plugin permission.
        
        Args:
            name: The name of the permission.
            description: A description of what the permission allows.
        """
        self.name = name
        self.description = description
    
    def __eq__(self, other):
        if isinstance(other, PluginPermission):
            return self.name == other.name
        return False
    
    def __hash__(self):
        return hash(self.name)

# Define standard permissions
PERMISSION_FILE_READ = PluginPermission(
    "file_read",
    "Read files from the file system"
)

PERMISSION_FILE_WRITE = PluginPermission(
    "file_write",
    "Write files to the file system"
)

PERMISSION_NETWORK = PluginPermission(
    "network",
    "Access the network"
)

PERMISSION_PROCESS = PluginPermission(
    "process",
    "Start or interact with system processes"
)

PERMISSION_UI = PluginPermission(
    "ui",
    "Create or modify UI elements"
)

PERMISSION_SYSTEM = PluginPermission(
    "system",
    "Access system information and resources"
)

PERMISSION_PLUGIN = PluginPermission(
    "plugin",
    "Interact with other plugins"
)

# All available permissions
ALL_PERMISSIONS = {
    PERMISSION_FILE_READ,
    PERMISSION_FILE_WRITE,
    PERMISSION_NETWORK,
    PERMISSION_PROCESS,
    PERMISSION_UI,
    PERMISSION_SYSTEM,
    PERMISSION_PLUGIN
}

class ResourceLimits:
    """
    Represents resource limits for a plugin.
    
    Resource limits control how much system resources a plugin can use,
    such as memory, CPU time, and file handles.
    """
    
    def __init__(
        self,
        max_memory_mb: int = 100,
        max_cpu_time_sec: int = 10,
        max_file_handles: int = 10,
        max_network_connections: int = 5
    ):
        """
        Initialize resource limits.
        
        Args:
            max_memory_mb: Maximum memory usage in MB.
            max_cpu_time_sec: Maximum CPU time in seconds.
            max_file_handles: Maximum number of open file handles.
            max_network_connections: Maximum number of network connections.
        """
        self.max_memory_mb = max_memory_mb
        self.max_cpu_time_sec = max_cpu_time_sec
        self.max_file_handles = max_file_handles
        self.max_network_connections = max_network_connections

class PluginSandbox:
    """
    Provides a sandboxed environment for running plugins.
    
    The sandbox restricts plugin access to system resources based on
    the permissions granted to the plugin and enforces resource limits.
    """
    
    def __init__(
        self,
        plugin_id: str,
        permissions: Set[PluginPermission] = None,
        resource_limits: ResourceLimits = None,
        allowed_modules: Set[str] = None
    ):
        """
        Initialize the plugin sandbox.
        
        Args:
            plugin_id: The ID of the plugin.
            permissions: The set of permissions granted to the plugin.
            resource_limits: The resource limits for the plugin.
            allowed_modules: The set of modules the plugin is allowed to import.
        """
        self.plugin_id = plugin_id
        self.permissions = permissions or set()
        self.resource_limits = resource_limits or ResourceLimits()
        self.allowed_modules = allowed_modules or {
            "builtins", "math", "random", "datetime", "json", "re", "collections",
            "itertools", "functools", "operator", "typing", "enum", "abc", "copy",
            "pathlib", "uuid", "hashlib", "base64", "struct", "io", "tempfile"
        }
        
        # Add the plugin's own module to allowed modules
        self.allowed_modules.add(f"plugins.{plugin_id}")
        
        # Track resource usage
        self.start_time = None
        self.memory_usage = 0
        self.open_file_handles = set()
        self.network_connections = set()
        
        # Plugin module and instance
        self.plugin_module = None
        self.plugin_instance = None
        
        logger.info(f"Initialized sandbox for plugin {plugin_id}")
    
    def has_permission(self, permission: PluginPermission) -> bool:
        """
        Check if the plugin has a specific permission.
        
        Args:
            permission: The permission to check.
            
        Returns:
            bool: True if the plugin has the permission, False otherwise.
        """
        return permission in self.permissions
    
    def check_permission(self, permission: PluginPermission):
        """
        Check if the plugin has a specific permission and raise an exception if not.
        
        Args:
            permission: The permission to check.
            
        Raises:
            PermissionDeniedError: If the plugin does not have the permission.
        """
        if not self.has_permission(permission):
            logger.warning(f"Plugin {self.plugin_id} attempted to use {permission.name} permission without authorization")
            raise PermissionDeniedError(f"Plugin {self.plugin_id} does not have permission: {permission.name}")
    
    def _create_restricted_builtins(self) -> Dict[str, Any]:
        """
        Create a restricted version of the builtins module.
        
        Returns:
            Dict[str, Any]: A dictionary of restricted builtins.
        """
        # Start with a copy of the builtins
        restricted_builtins = dict(__builtins__) if isinstance(__builtins__, dict) else dict(dir(__builtins__))
        
        # Remove dangerous functions
        dangerous_builtins = {
            "exec", "eval", "compile", "__import__", "open", "input",
            "memoryview", "globals", "locals", "vars", "dir", "getattr",
            "setattr", "delattr", "hasattr", "type", "id", "object", "help"
        }
        
        for func in dangerous_builtins:
            if func in restricted_builtins:
                del restricted_builtins[func]
        
        # Replace open with a restricted version
        restricted_builtins["open"] = self._restricted_open
        
        return restricted_builtins
    
    def _restricted_open(self, file, mode="r", *args, **kwargs):
        """
        A restricted version of the built-in open function.
        
        Args:
            file: The file to open.
            mode: The mode to open the file in.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            The opened file.
            
        Raises:
            PermissionDeniedError: If the plugin does not have the required permission.
        """
        # Check if the plugin has the required permission
        if "r" in mode or "+" in mode:
            self.check_permission(PERMISSION_FILE_READ)
        if "w" in mode or "a" in mode or "+" in mode or "x" in mode:
            self.check_permission(PERMISSION_FILE_WRITE)
        
        # Check if the plugin has exceeded the file handle limit
        if len(self.open_file_handles) >= self.resource_limits.max_file_handles:
            raise PluginSandboxError(f"Plugin {self.plugin_id} has exceeded the maximum number of file handles")
        
        # Open the file
        file_obj = open(file, mode, *args, **kwargs)
        
        # Track the file handle
        self.open_file_handles.add(file_obj)
        
        # Return a wrapper that removes the file handle from tracking when closed
        class FileWrapper:
            def __init__(self, file_obj, sandbox):
                self.file_obj = file_obj
                self.sandbox = sandbox
            
            def __getattr__(self, name):
                return getattr(self.file_obj, name)
            
            def close(self):
                self.file_obj.close()
                self.sandbox.open_file_handles.remove(self.file_obj)
            
            def __enter__(self):
                return self.file_obj.__enter__()
            
            def __exit__(self, *args):
                result = self.file_obj.__exit__(*args)
                self.sandbox.open_file_handles.remove(self.file_obj)
                return result
        
        return FileWrapper(file_obj, self)
    
    def _restricted_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """
        A restricted version of the built-in __import__ function.
        
        Args:
            name: The name of the module to import.
            globals: The global namespace.
            locals: The local namespace.
            fromlist: The list of names to import from the module.
            level: The level of relative imports.
            
        Returns:
            The imported module.
            
        Raises:
            PermissionDeniedError: If the plugin attempts to import a module that is not allowed.
        """
        # Check if the module is allowed
        if name not in self.allowed_modules:
            logger.warning(f"Plugin {self.plugin_id} attempted to import disallowed module: {name}")
            raise PermissionDeniedError(f"Plugin {self.plugin_id} is not allowed to import module: {name}")
        
        # Import the module
        return importlib.__import__(name, globals, locals, fromlist, level)
    
    def _create_sandbox_globals(self) -> Dict[str, Any]:
        """
        Create a sandboxed global namespace for the plugin.
        
        Returns:
            Dict[str, Any]: A dictionary of sandboxed globals.
        """
        # Create a restricted version of the builtins
        restricted_builtins = self._create_restricted_builtins()
        
        # Create a sandboxed globals dictionary
        sandbox_globals = {
            "__builtins__": restricted_builtins,
            "__name__": f"plugins.{self.plugin_id}",
            "__file__": None,
            "__package__": "plugins",
            "__import__": self._restricted_import,
            "__sandbox__": self
        }
        
        return sandbox_globals
    
    def load_plugin(self, plugin_path: str) -> Any:
        """
        Load a plugin into the sandbox.
        
        Args:
            plugin_path: The path to the plugin file.
            
        Returns:
            Any: The plugin instance.
            
        Raises:
            PluginSandboxError: If there's an error loading the plugin.
        """
        try:
            # Record the start time
            self.start_time = time.time()
            
            # Create a spec for the module
            spec = importlib.util.spec_from_file_location(f"plugins.{self.plugin_id}", plugin_path)
            if not spec or not spec.loader:
                raise PluginSandboxError(f"Failed to create spec for plugin {self.plugin_id}")
            
            # Create a module from the spec
            module = importlib.util.module_from_spec(spec)
            
            # Set up the module's globals
            module.__dict__.update(self._create_sandbox_globals())
            
            # Execute the module
            spec.loader.exec_module(module)
            
            # Store the module
            self.plugin_module = module
            
            # Find the plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and attr.__module__ == module.__name__:
                    # Check if the class has an activate method
                    if hasattr(attr, "activate") and callable(getattr(attr, "activate")):
                        plugin_class = attr
                        break
            
            if not plugin_class:
                raise PluginSandboxError(f"No plugin class found in {self.plugin_id}")
            
            # Create an instance of the plugin class
            self.plugin_instance = plugin_class()
            
            logger.info(f"Successfully loaded plugin {self.plugin_id}")
            
            return self.plugin_instance
        except Exception as e:
            logger.error(f"Error loading plugin {self.plugin_id}: {e}", exc_info=True)
            raise PluginSandboxError(f"Error loading plugin {self.plugin_id}: {str(e)}")
    
    def activate_plugin(self, app=None) -> bool:
        """
        Activate the plugin.
        
        Args:
            app: The application instance to pass to the plugin's activate method.
            
        Returns:
            bool: True if the plugin was activated successfully, False otherwise.
        """
        if not self.plugin_instance:
            logger.error(f"Cannot activate plugin {self.plugin_id}: Plugin not loaded")
            return False
        
        try:
            # Check if we've exceeded the CPU time limit
            if time.time() - self.start_time > self.resource_limits.max_cpu_time_sec:
                logger.warning(f"Plugin {self.plugin_id} has exceeded the CPU time limit")
                raise PluginSandboxError(f"Plugin {self.plugin_id} has exceeded the CPU time limit")
            
            # Activate the plugin
            result = self.plugin_instance.activate(app)
            
            logger.info(f"Successfully activated plugin {self.plugin_id}")
            
            return result
        except Exception as e:
            logger.error(f"Error activating plugin {self.plugin_id}: {e}", exc_info=True)
            return False
    
    def deactivate_plugin(self) -> bool:
        """
        Deactivate the plugin.
        
        Returns:
            bool: True if the plugin was deactivated successfully, False otherwise.
        """
        if not self.plugin_instance:
            logger.error(f"Cannot deactivate plugin {self.plugin_id}: Plugin not loaded")
            return False
        
        try:
            # Check if the plugin has a deactivate method
            if hasattr(self.plugin_instance, "deactivate") and callable(getattr(self.plugin_instance, "deactivate")):
                # Deactivate the plugin
                self.plugin_instance.deactivate()
            
            # Clean up resources
            for file_handle in self.open_file_handles:
                try:
                    file_handle.close()
                except:
                    pass
            
            self.open_file_handles.clear()
            
            logger.info(f"Successfully deactivated plugin {self.plugin_id}")
            
            return True
        except Exception as e:
            logger.error(f"Error deactivating plugin {self.plugin_id}: {e}", exc_info=True)
            return False

class PluginSandboxManager:
    """
    Manages sandboxed plugins.
    
    This class is responsible for creating, loading, activating, and
    deactivating sandboxed plugins, as well as managing their permissions
    and resource limits.
    """
    
    def __init__(self):
        """Initialize the plugin sandbox manager."""
        self.sandboxes = {}
        self.plugin_permissions = {}
        self.plugin_resource_limits = {}
        self.plugin_allowed_modules = {}
    
    def register_plugin(
        self,
        plugin_id: str,
        permissions: Set[PluginPermission] = None,
        resource_limits: ResourceLimits = None,
        allowed_modules: Set[str] = None
    ):
        """
        Register a plugin with the sandbox manager.
        
        Args:
            plugin_id: The ID of the plugin.
            permissions: The set of permissions granted to the plugin.
            resource_limits: The resource limits for the plugin.
            allowed_modules: The set of modules the plugin is allowed to import.
        """
        self.plugin_permissions[plugin_id] = permissions or set()
        self.plugin_resource_limits[plugin_id] = resource_limits or ResourceLimits()
        self.plugin_allowed_modules[plugin_id] = allowed_modules or set()
        
        logger.info(f"Registered plugin {plugin_id} with {len(self.plugin_permissions[plugin_id])} permissions")
    
    def create_sandbox(self, plugin_id: str) -> PluginSandbox:
        """
        Create a sandbox for a plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            
        Returns:
            PluginSandbox: The created sandbox.
            
        Raises:
            PluginSandboxError: If the plugin is not registered.
        """
        if plugin_id not in self.plugin_permissions:
            logger.error(f"Cannot create sandbox for plugin {plugin_id}: Plugin not registered")
            raise PluginSandboxError(f"Plugin {plugin_id} is not registered")
        
        sandbox = PluginSandbox(
            plugin_id,
            self.plugin_permissions[plugin_id],
            self.plugin_resource_limits[plugin_id],
            self.plugin_allowed_modules[plugin_id]
        )
        
        self.sandboxes[plugin_id] = sandbox
        
        logger.info(f"Created sandbox for plugin {plugin_id}")
        
        return sandbox
    
    def load_plugin(self, plugin_id: str, plugin_path: str) -> Any:
        """
        Load a plugin into a sandbox.
        
        Args:
            plugin_id: The ID of the plugin.
            plugin_path: The path to the plugin file.
            
        Returns:
            Any: The plugin instance.
            
        Raises:
            PluginSandboxError: If there's an error loading the plugin.
        """
        # Create a sandbox if one doesn't exist
        if plugin_id not in self.sandboxes:
            self.create_sandbox(plugin_id)
        
        # Load the plugin
        return self.sandboxes[plugin_id].load_plugin(plugin_path)
    
    def activate_plugin(self, plugin_id: str, app=None) -> bool:
        """
        Activate a plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            app: The application instance to pass to the plugin's activate method.
            
        Returns:
            bool: True if the plugin was activated successfully, False otherwise.
            
        Raises:
            PluginSandboxError: If the plugin is not loaded.
        """
        if plugin_id not in self.sandboxes:
            logger.error(f"Cannot activate plugin {plugin_id}: Plugin not loaded")
            raise PluginSandboxError(f"Plugin {plugin_id} is not loaded")
        
        return self.sandboxes[plugin_id].activate_plugin(app)
    
    def deactivate_plugin(self, plugin_id: str) -> bool:
        """
        Deactivate a plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            
        Returns:
            bool: True if the plugin was deactivated successfully, False otherwise.
            
        Raises:
            PluginSandboxError: If the plugin is not loaded.
        """
        if plugin_id not in self.sandboxes:
            logger.error(f"Cannot deactivate plugin {plugin_id}: Plugin not loaded")
            raise PluginSandboxError(f"Plugin {plugin_id} is not loaded")
        
        return self.sandboxes[plugin_id].deactivate_plugin()
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            
        Returns:
            bool: True if the plugin was unloaded successfully, False otherwise.
        """
        if plugin_id not in self.sandboxes:
            logger.warning(f"Cannot unload plugin {plugin_id}: Plugin not loaded")
            return False
        
        try:
            # Deactivate the plugin
            self.deactivate_plugin(plugin_id)
            
            # Remove the sandbox
            del self.sandboxes[plugin_id]
            
            logger.info(f"Unloaded plugin {plugin_id}")
            
            return True
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}", exc_info=True)
            return False
    
    def get_plugin_permissions(self, plugin_id: str) -> Set[PluginPermission]:
        """
        Get the permissions granted to a plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            
        Returns:
            Set[PluginPermission]: The set of permissions granted to the plugin.
            
        Raises:
            PluginSandboxError: If the plugin is not registered.
        """
        if plugin_id not in self.plugin_permissions:
            logger.error(f"Cannot get permissions for plugin {plugin_id}: Plugin not registered")
            raise PluginSandboxError(f"Plugin {plugin_id} is not registered")
        
        return self.plugin_permissions[plugin_id]
    
    def grant_permission(self, plugin_id: str, permission: PluginPermission) -> bool:
        """
        Grant a permission to a plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            permission: The permission to grant.
            
        Returns:
            bool: True if the permission was granted successfully, False otherwise.
            
        Raises:
            PluginSandboxError: If the plugin is not registered.
        """
        if plugin_id not in self.plugin_permissions:
            logger.error(f"Cannot grant permission to plugin {plugin_id}: Plugin not registered")
            raise PluginSandboxError(f"Plugin {plugin_id} is not registered")
        
        self.plugin_permissions[plugin_id].add(permission)
        
        # Update the sandbox if it exists
        if plugin_id in self.sandboxes:
            self.sandboxes[plugin_id].permissions.add(permission)
        
        logger.info(f"Granted permission {permission.name} to plugin {plugin_id}")
        
        return True
    
    def revoke_permission(self, plugin_id: str, permission: PluginPermission) -> bool:
        """
        Revoke a permission from a plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            permission: The permission to revoke.
            
        Returns:
            bool: True if the permission was revoked successfully, False otherwise.
            
        Raises:
            PluginSandboxError: If the plugin is not registered.
        """
        if plugin_id not in self.plugin_permissions:
            logger.error(f"Cannot revoke permission from plugin {plugin_id}: Plugin not registered")
            raise PluginSandboxError(f"Plugin {plugin_id} is not registered")
        
        if permission in self.plugin_permissions[plugin_id]:
            self.plugin_permissions[plugin_id].remove(permission)
            
            # Update the sandbox if it exists
            if plugin_id in self.sandboxes:
                self.sandboxes[plugin_id].permissions.remove(permission)
            
            logger.info(f"Revoked permission {permission.name} from plugin {plugin_id}")
            
            return True
        
        return False
    
    def set_resource_limits(self, plugin_id: str, resource_limits: ResourceLimits) -> bool:
        """
        Set the resource limits for a plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            resource_limits: The resource limits to set.
            
        Returns:
            bool: True if the resource limits were set successfully, False otherwise.
            
        Raises:
            PluginSandboxError: If the plugin is not registered.
        """
        if plugin_id not in self.plugin_resource_limits:
            logger.error(f"Cannot set resource limits for plugin {plugin_id}: Plugin not registered")
            raise PluginSandboxError(f"Plugin {plugin_id} is not registered")
        
        self.plugin_resource_limits[plugin_id] = resource_limits
        
        # Update the sandbox if it exists
        if plugin_id in self.sandboxes:
            self.sandboxes[plugin_id].resource_limits = resource_limits
        
        logger.info(f"Set resource limits for plugin {plugin_id}")
        
        return True
    
    def add_allowed_module(self, plugin_id: str, module_name: str) -> bool:
        """
        Add a module to the list of modules a plugin is allowed to import.
        
        Args:
            plugin_id: The ID of the plugin.
            module_name: The name of the module to allow.
            
        Returns:
            bool: True if the module was added successfully, False otherwise.
            
        Raises:
            PluginSandboxError: If the plugin is not registered.
        """
        if plugin_id not in self.plugin_allowed_modules:
            logger.error(f"Cannot add allowed module for plugin {plugin_id}: Plugin not registered")
            raise PluginSandboxError(f"Plugin {plugin_id} is not registered")
        
        self.plugin_allowed_modules[plugin_id].add(module_name)
        
        # Update the sandbox if it exists
        if plugin_id in self.sandboxes:
            self.sandboxes[plugin_id].allowed_modules.add(module_name)
        
        logger.info(f"Added allowed module {module_name} for plugin {plugin_id}")
        
        return True
    
    def remove_allowed_module(self, plugin_id: str, module_name: str) -> bool:
        """
        Remove a module from the list of modules a plugin is allowed to import.
        
        Args:
            plugin_id: The ID of the plugin.
            module_name: The name of the module to disallow.
            
        Returns:
            bool: True if the module was removed successfully, False otherwise.
            
        Raises:
            PluginSandboxError: If the plugin is not registered.
        """
        if plugin_id not in self.plugin_allowed_modules:
            logger.error(f"Cannot remove allowed module for plugin {plugin_id}: Plugin not registered")
            raise PluginSandboxError(f"Plugin {plugin_id} is not registered")
        
        if module_name in self.plugin_allowed_modules[plugin_id]:
            self.plugin_allowed_modules[plugin_id].remove(module_name)
            
            # Update the sandbox if it exists
            if plugin_id in self.sandboxes:
                self.sandboxes[plugin_id].allowed_modules.remove(module_name)
            
            logger.info(f"Removed allowed module {module_name} for plugin {plugin_id}")
            
            return True
        
        return False
