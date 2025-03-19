"""
Plugin manager for RebelDESK.

This module provides a plugin manager for loading, activating, and managing
plugins in RebelDESK. It uses the plugin sandbox system to enhance security
by restricting plugin access to system resources.
"""

import os
import sys
import logging
import importlib
import importlib.util
import json
from typing import Dict, Any, Optional, List, Set, Callable, Tuple, Union
from pathlib import Path

from .plugin_sandbox import (
    PluginSandboxManager, PluginPermission, ResourceLimits,
    PERMISSION_FILE_READ, PERMISSION_FILE_WRITE, PERMISSION_NETWORK,
    PERMISSION_PROCESS, PERMISSION_UI, PERMISSION_SYSTEM, PERMISSION_PLUGIN,
    PermissionDeniedError, PluginSandboxError
)

logger = logging.getLogger(__name__)

class PluginMetadata:
    """
    Metadata for a plugin.
    
    This class represents the metadata for a plugin, including its ID, name,
    version, description, author, and dependencies.
    """
    
    def __init__(
        self,
        plugin_id: str,
        name: str,
        version: str,
        description: str = "",
        author: str = "",
        dependencies: List[str] = None,
        permissions: List[str] = None,
        min_app_version: str = "0.1.0",
        max_app_version: str = None,
        homepage: str = "",
        repository: str = "",
        tags: List[str] = None
    ):
        """
        Initialize the plugin metadata.
        
        Args:
            plugin_id: The ID of the plugin.
            name: The name of the plugin.
            version: The version of the plugin.
            description: A description of the plugin.
            author: The author of the plugin.
            dependencies: A list of plugin IDs that this plugin depends on.
            permissions: A list of permissions that this plugin requires.
            min_app_version: The minimum app version required by the plugin.
            max_app_version: The maximum app version supported by the plugin.
            homepage: The homepage URL of the plugin.
            repository: The repository URL of the plugin.
            tags: A list of tags for the plugin.
        """
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.dependencies = dependencies or []
        self.permissions = permissions or []
        self.min_app_version = min_app_version
        self.max_app_version = max_app_version
        self.homepage = homepage
        self.repository = repository
        self.tags = tags or []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        """
        Create a PluginMetadata instance from a dictionary.
        
        Args:
            data: A dictionary containing the plugin metadata.
            
        Returns:
            PluginMetadata: A new PluginMetadata instance.
            
        Raises:
            ValueError: If the dictionary is missing required fields.
        """
        required_fields = ["plugin_id", "name", "version"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return cls(
            plugin_id=data["plugin_id"],
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            dependencies=data.get("dependencies", []),
            permissions=data.get("permissions", []),
            min_app_version=data.get("min_app_version", "0.1.0"),
            max_app_version=data.get("max_app_version"),
            homepage=data.get("homepage", ""),
            repository=data.get("repository", ""),
            tags=data.get("tags", [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the plugin metadata to a dictionary.
        
        Returns:
            Dict[str, Any]: A dictionary containing the plugin metadata.
        """
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies,
            "permissions": self.permissions,
            "min_app_version": self.min_app_version,
            "max_app_version": self.max_app_version,
            "homepage": self.homepage,
            "repository": self.repository,
            "tags": self.tags
        }

class PluginManager:
    """
    Plugin manager for RebelDESK.
    
    This class is responsible for loading, activating, and managing plugins
    in RebelDESK. It uses the plugin sandbox system to enhance security by
    restricting plugin access to system resources.
    """
    
    def __init__(self, app=None):
        """
        Initialize the plugin manager.
        
        Args:
            app: The application instance.
        """
        self.app = app
        self.plugin_dirs = []
        self.plugins = {}
        self.active_plugins = set()
        self.plugin_metadata = {}
        self.sandbox_manager = PluginSandboxManager()
        
        # Add default plugin directories
        self._add_default_plugin_dirs()
        
        logger.info("Plugin manager initialized")
    
    def _add_default_plugin_dirs(self):
        """Add default plugin directories."""
        # Add the built-in plugins directory
        built_in_dir = os.path.join(os.path.dirname(__file__), "built_in")
        if os.path.exists(built_in_dir):
            self.add_plugin_dir(built_in_dir)
        
        # Add the user plugins directory
        user_dir = os.path.expanduser("~/.rebeldesk/plugins")
        if os.path.exists(user_dir):
            self.add_plugin_dir(user_dir)
        
        # Add the system plugins directory
        system_dir = "/usr/share/rebeldesk/plugins"
        if os.path.exists(system_dir):
            self.add_plugin_dir(system_dir)
    
    def add_plugin_dir(self, plugin_dir: str):
        """
        Add a directory to search for plugins.
        
        Args:
            plugin_dir: The directory to add.
        """
        if os.path.exists(plugin_dir) and os.path.isdir(plugin_dir):
            if plugin_dir not in self.plugin_dirs:
                self.plugin_dirs.append(plugin_dir)
                logger.info(f"Added plugin directory: {plugin_dir}")
        else:
            logger.warning(f"Plugin directory does not exist: {plugin_dir}")
    
    def discover_plugins(self) -> Dict[str, PluginMetadata]:
        """
        Discover plugins in the plugin directories.
        
        Returns:
            Dict[str, PluginMetadata]: A dictionary mapping plugin IDs to metadata.
        """
        discovered_plugins = {}
        
        for plugin_dir in self.plugin_dirs:
            # Check if the directory exists
            if not os.path.exists(plugin_dir):
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
                continue
            
            # Iterate over subdirectories
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                
                # Skip non-directories
                if not os.path.isdir(item_path):
                    continue
                
                # Check for plugin.json
                metadata_path = os.path.join(item_path, "plugin.json")
                if not os.path.exists(metadata_path):
                    logger.debug(f"Skipping directory without plugin.json: {item_path}")
                    continue
                
                try:
                    # Load metadata
                    with open(metadata_path, "r") as f:
                        metadata_dict = json.load(f)
                    
                    # Create metadata object
                    metadata = PluginMetadata.from_dict(metadata_dict)
                    
                    # Check for main.py
                    main_path = os.path.join(item_path, "main.py")
                    if not os.path.exists(main_path):
                        logger.warning(f"Plugin {metadata.plugin_id} is missing main.py")
                        continue
                    
                    # Add to discovered plugins
                    discovered_plugins[metadata.plugin_id] = metadata
                    
                    logger.info(f"Discovered plugin: {metadata.plugin_id} ({metadata.name} v{metadata.version})")
                except Exception as e:
                    logger.error(f"Error loading plugin metadata from {metadata_path}: {e}", exc_info=True)
        
        return discovered_plugins
    
    def _get_plugin_path(self, plugin_id: str) -> Optional[str]:
        """
        Get the path to a plugin's main.py file.
        
        Args:
            plugin_id: The ID of the plugin.
            
        Returns:
            Optional[str]: The path to the plugin's main.py file, or None if not found.
        """
        for plugin_dir in self.plugin_dirs:
            # Check for plugin directory
            plugin_path = os.path.join(plugin_dir, plugin_id)
            if not os.path.exists(plugin_path) or not os.path.isdir(plugin_path):
                continue
            
            # Check for main.py
            main_path = os.path.join(plugin_path, "main.py")
            if os.path.exists(main_path):
                return main_path
        
        return None
    
    def _get_plugin_metadata_path(self, plugin_id: str) -> Optional[str]:
        """
        Get the path to a plugin's metadata file.
        
        Args:
            plugin_id: The ID of the plugin.
            
        Returns:
            Optional[str]: The path to the plugin's metadata file, or None if not found.
        """
        for plugin_dir in self.plugin_dirs:
            # Check for plugin directory
            plugin_path = os.path.join(plugin_dir, plugin_id)
            if not os.path.exists(plugin_path) or not os.path.isdir(plugin_path):
                continue
            
            # Check for plugin.json
            metadata_path = os.path.join(plugin_path, "plugin.json")
            if os.path.exists(metadata_path):
                return metadata_path
        
        return None
    
    def _load_plugin_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """
        Load the metadata for a plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            
        Returns:
            Optional[PluginMetadata]: The plugin metadata, or None if not found.
        """
        metadata_path = self._get_plugin_metadata_path(plugin_id)
        if not metadata_path:
            logger.error(f"Plugin metadata not found: {plugin_id}")
            return None
        
        try:
            with open(metadata_path, "r") as f:
                metadata_dict = json.load(f)
            
            return PluginMetadata.from_dict(metadata_dict)
        except Exception as e:
            logger.error(f"Error loading plugin metadata for {plugin_id}: {e}", exc_info=True)
            return None
    
    def _register_plugin_with_sandbox(self, plugin_id: str, metadata: PluginMetadata):
        """
        Register a plugin with the sandbox manager.
        
        Args:
            plugin_id: The ID of the plugin.
            metadata: The plugin metadata.
        """
        # Convert permission strings to PluginPermission objects
        permissions = set()
        for permission_name in metadata.permissions:
            if permission_name == "file_read":
                permissions.add(PERMISSION_FILE_READ)
            elif permission_name == "file_write":
                permissions.add(PERMISSION_FILE_WRITE)
            elif permission_name == "network":
                permissions.add(PERMISSION_NETWORK)
            elif permission_name == "process":
                permissions.add(PERMISSION_PROCESS)
            elif permission_name == "ui":
                permissions.add(PERMISSION_UI)
            elif permission_name == "system":
                permissions.add(PERMISSION_SYSTEM)
            elif permission_name == "plugin":
                permissions.add(PERMISSION_PLUGIN)
            else:
                logger.warning(f"Unknown permission: {permission_name}")
        
        # Create resource limits
        resource_limits = ResourceLimits()
        
        # Create allowed modules
        allowed_modules = {
            "builtins", "math", "random", "datetime", "json", "re", "collections",
            "itertools", "functools", "operator", "typing", "enum", "abc", "copy",
            "pathlib", "uuid", "hashlib", "base64", "struct", "io", "tempfile"
        }
        
        # Register the plugin with the sandbox manager
        self.sandbox_manager.register_plugin(
            plugin_id,
            permissions,
            resource_limits,
            allowed_modules
        )
        
        logger.info(f"Registered plugin {plugin_id} with sandbox manager")
    
    def load_plugin(self, plugin_id: str, resolve_dependencies: bool = True) -> bool:
        """
        Load a plugin by ID.
        
        Args:
            plugin_id: The ID of the plugin to load.
            resolve_dependencies: Whether to resolve dependencies. Defaults to True.
            
        Returns:
            bool: True if the plugin was loaded successfully, False otherwise.
        """
        if plugin_id in self.plugins:
            logger.debug(f"Plugin {plugin_id} is already loaded")
            return True
        
        # Load plugin metadata
        metadata = self._load_plugin_metadata(plugin_id)
        if not metadata:
            logger.error(f"Failed to load metadata for plugin {plugin_id}")
            return False
        
        # Store metadata
        self.plugin_metadata[plugin_id] = metadata
        
        # Resolve dependencies
        if resolve_dependencies:
            for dependency in metadata.dependencies:
                if dependency not in self.plugins:
                    logger.info(f"Loading dependency {dependency} for plugin {plugin_id}")
                    if not self.load_plugin(dependency, resolve_dependencies=True):
                        logger.error(f"Failed to load dependency {dependency} for plugin {plugin_id}")
                        return False
        
        # Get the plugin path
        plugin_path = self._get_plugin_path(plugin_id)
        if not plugin_path:
            logger.error(f"Plugin {plugin_id} not found")
            return False
        
        try:
            # Register the plugin with the sandbox manager
            self._register_plugin_with_sandbox(plugin_id, metadata)
            
            # Load the plugin in a sandbox
            plugin_instance = self.sandbox_manager.load_plugin(plugin_id, plugin_path)
            
            # Store the plugin instance
            self.plugins[plugin_id] = plugin_instance
            
            logger.info(f"Successfully loaded plugin {plugin_id}")
            
            return True
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {e}", exc_info=True)
            return False
    
    def activate_plugin(self, plugin_id: str) -> bool:
        """
        Activate a plugin.
        
        Args:
            plugin_id: The ID of the plugin to activate.
            
        Returns:
            bool: True if the plugin was activated successfully, False otherwise.
        """
        if plugin_id not in self.plugins:
            logger.error(f"Cannot activate plugin {plugin_id}: Plugin not loaded")
            return False
        
        if plugin_id in self.active_plugins:
            logger.debug(f"Plugin {plugin_id} is already active")
            return True
        
        try:
            # Activate the plugin in the sandbox
            result = self.sandbox_manager.activate_plugin(plugin_id, self.app)
            
            if result:
                # Add to active plugins
                self.active_plugins.add(plugin_id)
                logger.info(f"Successfully activated plugin {plugin_id}")
            else:
                logger.error(f"Failed to activate plugin {plugin_id}")
            
            return result
        except Exception as e:
            logger.error(f"Error activating plugin {plugin_id}: {e}", exc_info=True)
            return False
    
    def deactivate_plugin(self, plugin_id: str) -> bool:
        """
        Deactivate a plugin.
        
        Args:
            plugin_id: The ID of the plugin to deactivate.
            
        Returns:
            bool: True if the plugin was deactivated successfully, False otherwise.
        """
        if plugin_id not in self.plugins:
            logger.error(f"Cannot deactivate plugin {plugin_id}: Plugin not loaded")
            return False
        
        if plugin_id not in self.active_plugins:
            logger.debug(f"Plugin {plugin_id} is not active")
            return True
        
        try:
            # Deactivate the plugin in the sandbox
            result = self.sandbox_manager.deactivate_plugin(plugin_id)
            
            if result:
                # Remove from active plugins
                self.active_plugins.remove(plugin_id)
                logger.info(f"Successfully deactivated plugin {plugin_id}")
            else:
                logger.error(f"Failed to deactivate plugin {plugin_id}")
            
            return result
        except Exception as e:
            logger.error(f"Error deactivating plugin {plugin_id}: {e}", exc_info=True)
            return False
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_id: The ID of the plugin to unload.
            
        Returns:
            bool: True if the plugin was unloaded successfully, False otherwise.
        """
        if plugin_id not in self.plugins:
            logger.warning(f"Cannot unload plugin {plugin_id}: Plugin not loaded")
            return False
        
        # Check if the plugin is active
        if plugin_id in self.active_plugins:
            # Deactivate the plugin
            if not self.deactivate_plugin(plugin_id):
                logger.error(f"Failed to deactivate plugin {plugin_id} before unloading")
                return False
        
        try:
            # Unload the plugin from the sandbox
            result = self.sandbox_manager.unload_plugin(plugin_id)
            
            if result:
                # Remove from plugins
                del self.plugins[plugin_id]
                
                # Remove from metadata
                if plugin_id in self.plugin_metadata:
                    del self.plugin_metadata[plugin_id]
                
                logger.info(f"Successfully unloaded plugin {plugin_id}")
            else:
                logger.error(f"Failed to unload plugin {plugin_id}")
            
            return result
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}", exc_info=True)
            return False
    
    def get_plugin_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """
        Get the metadata for a plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            
        Returns:
            Optional[PluginMetadata]: The plugin metadata, or None if not found.
        """
        return self.plugin_metadata.get(plugin_id)
    
    def is_plugin_loaded(self, plugin_id: str) -> bool:
        """
        Check if a plugin is loaded.
        
        Args:
            plugin_id: The ID of the plugin.
            
        Returns:
            bool: True if the plugin is loaded, False otherwise.
        """
        return plugin_id in self.plugins
    
    def is_plugin_active(self, plugin_id: str) -> bool:
        """
        Check if a plugin is active.
        
        Args:
            plugin_id: The ID of the plugin.
            
        Returns:
            bool: True if the plugin is active, False otherwise.
        """
        return plugin_id in self.active_plugins
    
    def get_loaded_plugins(self) -> List[str]:
        """
        Get a list of loaded plugin IDs.
        
        Returns:
            List[str]: A list of loaded plugin IDs.
        """
        return list(self.plugins.keys())
    
    def get_active_plugins(self) -> List[str]:
        """
        Get a list of active plugin IDs.
        
        Returns:
            List[str]: A list of active plugin IDs.
        """
        return list(self.active_plugins)
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """
        Load all discovered plugins.
        
        Returns:
            Dict[str, bool]: A dictionary mapping plugin IDs to load success.
        """
        results = {}
        
        # Discover plugins
        discovered_plugins = self.discover_plugins()
        
        # Load each plugin
        for plugin_id in discovered_plugins:
            results[plugin_id] = self.load_plugin(plugin_id)
        
        return results
    
    def activate_all_plugins(self) -> Dict[str, bool]:
        """
        Activate all loaded plugins.
        
        Returns:
            Dict[str, bool]: A dictionary mapping plugin IDs to activation success.
        """
        results = {}
        
        # Activate each loaded plugin
        for plugin_id in self.get_loaded_plugins():
            results[plugin_id] = self.activate_plugin(plugin_id)
        
        return results
    
    def deactivate_all_plugins(self) -> Dict[str, bool]:
        """
        Deactivate all active plugins.
        
        Returns:
            Dict[str, bool]: A dictionary mapping plugin IDs to deactivation success.
        """
        results = {}
        
        # Deactivate each active plugin
        for plugin_id in self.get_active_plugins():
            results[plugin_id] = self.deactivate_plugin(plugin_id)
        
        return results
    
    def unload_all_plugins(self) -> Dict[str, bool]:
        """
        Unload all loaded plugins.
        
        Returns:
            Dict[str, bool]: A dictionary mapping plugin IDs to unload success.
        """
        results = {}
        
        # Unload each loaded plugin
        for plugin_id in self.get_loaded_plugins():
            results[plugin_id] = self.unload_plugin(plugin_id)
        
        return results
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """
        Reload a plugin.
        
        Args:
            plugin_id: The ID of the plugin to reload.
            
        Returns:
            bool: True if the plugin was reloaded successfully, False otherwise.
        """
        # Check if the plugin is loaded
        if plugin_id not in self.plugins:
            logger.warning(f"Cannot reload plugin {plugin_id}: Plugin not loaded")
            return self.load_plugin(plugin_id)
        
        # Check if the plugin is active
        was_active = plugin_id in self.active_plugins
        
        # Unload the plugin
        if not self.unload_plugin(plugin_id):
            logger.error(f"Failed to unload plugin {plugin_id} during reload")
            return False
        
        # Load the plugin
        if not self.load_plugin(plugin_id):
            logger.error(f"Failed to load plugin {plugin_id} during reload")
            return False
        
        # Activate the plugin if it was active
        if was_active:
            if not self.activate_plugin(plugin_id):
                logger.error(f"Failed to activate plugin {plugin_id} during reload")
                return False
        
        logger.info(f"Successfully reloaded plugin {plugin_id}")
        
        return True
