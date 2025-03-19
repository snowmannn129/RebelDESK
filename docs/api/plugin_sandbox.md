# Plugin Sandbox API Reference

This document provides a reference for the RebelDESK Plugin Sandbox API, which includes the `PluginSandbox` and `PluginSandboxManager` classes. The plugin sandbox system enhances security by restricting plugin access to system resources and isolating plugins from each other and the main application.

## Overview

The plugin sandbox system provides the following features:

- **Permission-based access control**: Plugins must request specific permissions to access system resources.
- **Resource limits**: Plugins are limited in the amount of system resources they can use.
- **Module restrictions**: Plugins can only import modules that are explicitly allowed.
- **Isolation**: Plugins are isolated from each other and the main application.
- **Secure loading and execution**: Plugins are loaded and executed in a controlled environment.

## PluginPermission

The `PluginPermission` class represents a permission that can be granted to a plugin. Permissions control what actions a plugin is allowed to perform, such as accessing the file system, network, or system resources.

### Class Definition

```python
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
```

### Standard Permissions

The following standard permissions are defined:

- `PERMISSION_FILE_READ`: Read files from the file system.
- `PERMISSION_FILE_WRITE`: Write files to the file system.
- `PERMISSION_NETWORK`: Access the network.
- `PERMISSION_PROCESS`: Start or interact with system processes.
- `PERMISSION_UI`: Create or modify UI elements.
- `PERMISSION_SYSTEM`: Access system information and resources.
- `PERMISSION_PLUGIN`: Interact with other plugins.

## ResourceLimits

The `ResourceLimits` class represents resource limits for a plugin. Resource limits control how much system resources a plugin can use, such as memory, CPU time, and file handles.

### Class Definition

```python
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
```

## PluginSandbox

The `PluginSandbox` class provides a sandboxed environment for running plugins. The sandbox restricts plugin access to system resources based on the permissions granted to the plugin and enforces resource limits.

### Class Definition

```python
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
```

### Methods

#### `has_permission(permission: PluginPermission) -> bool`

Check if the plugin has a specific permission.

**Args**:
- `permission`: The permission to check.

**Returns**:
- `bool`: True if the plugin has the permission, False otherwise.

#### `check_permission(permission: PluginPermission)`

Check if the plugin has a specific permission and raise an exception if not.

**Args**:
- `permission`: The permission to check.

**Raises**:
- `PermissionDeniedError`: If the plugin does not have the permission.

#### `load_plugin(plugin_path: str) -> Any`

Load a plugin into the sandbox.

**Args**:
- `plugin_path`: The path to the plugin file.

**Returns**:
- `Any`: The plugin instance.

**Raises**:
- `PluginSandboxError`: If there's an error loading the plugin.

#### `activate_plugin(app=None) -> bool`

Activate the plugin.

**Args**:
- `app`: The application instance to pass to the plugin's activate method.

**Returns**:
- `bool`: True if the plugin was activated successfully, False otherwise.

#### `deactivate_plugin() -> bool`

Deactivate the plugin.

**Returns**:
- `bool`: True if the plugin was deactivated successfully, False otherwise.

## PluginSandboxManager

The `PluginSandboxManager` class manages sandboxed plugins. This class is responsible for creating, loading, activating, and deactivating sandboxed plugins, as well as managing their permissions and resource limits.

### Class Definition

```python
class PluginSandboxManager:
    """
    Manages sandboxed plugins.
    
    This class is responsible for creating, loading, activating, and
    deactivating sandboxed plugins, as well as managing their permissions
    and resource limits.
    """
    
    def __init__(self):
        """Initialize the plugin sandbox manager."""
```

### Methods

#### `register_plugin(plugin_id: str, permissions: Set[PluginPermission] = None, resource_limits: ResourceLimits = None, allowed_modules: Set[str] = None)`

Register a plugin with the sandbox manager.

**Args**:
- `plugin_id`: The ID of the plugin.
- `permissions`: The set of permissions granted to the plugin.
- `resource_limits`: The resource limits for the plugin.
- `allowed_modules`: The set of modules the plugin is allowed to import.

#### `create_sandbox(plugin_id: str) -> PluginSandbox`

Create a sandbox for a plugin.

**Args**:
- `plugin_id`: The ID of the plugin.

**Returns**:
- `PluginSandbox`: The created sandbox.

**Raises**:
- `PluginSandboxError`: If the plugin is not registered.

#### `load_plugin(plugin_id: str, plugin_path: str) -> Any`

Load a plugin into a sandbox.

**Args**:
- `plugin_id`: The ID of the plugin.
- `plugin_path`: The path to the plugin file.

**Returns**:
- `Any`: The plugin instance.

**Raises**:
- `PluginSandboxError`: If there's an error loading the plugin.

#### `activate_plugin(plugin_id: str, app=None) -> bool`

Activate a plugin.

**Args**:
- `plugin_id`: The ID of the plugin.
- `app`: The application instance to pass to the plugin's activate method.

**Returns**:
- `bool`: True if the plugin was activated successfully, False otherwise.

**Raises**:
- `PluginSandboxError`: If the plugin is not loaded.

#### `deactivate_plugin(plugin_id: str) -> bool`

Deactivate a plugin.

**Args**:
- `plugin_id`: The ID of the plugin.

**Returns**:
- `bool`: True if the plugin was deactivated successfully, False otherwise.

**Raises**:
- `PluginSandboxError`: If the plugin is not loaded.

#### `unload_plugin(plugin_id: str) -> bool`

Unload a plugin.

**Args**:
- `plugin_id`: The ID of the plugin.

**Returns**:
- `bool`: True if the plugin was unloaded successfully, False otherwise.

#### `get_plugin_permissions(plugin_id: str) -> Set[PluginPermission]`

Get the permissions granted to a plugin.

**Args**:
- `plugin_id`: The ID of the plugin.

**Returns**:
- `Set[PluginPermission]`: The set of permissions granted to the plugin.

**Raises**:
- `PluginSandboxError`: If the plugin is not registered.

#### `grant_permission(plugin_id: str, permission: PluginPermission) -> bool`

Grant a permission to a plugin.

**Args**:
- `plugin_id`: The ID of the plugin.
- `permission`: The permission to grant.

**Returns**:
- `bool`: True if the permission was granted successfully, False otherwise.

**Raises**:
- `PluginSandboxError`: If the plugin is not registered.

#### `revoke_permission(plugin_id: str, permission: PluginPermission) -> bool`

Revoke a permission from a plugin.

**Args**:
- `plugin_id`: The ID of the plugin.
- `permission`: The permission to revoke.

**Returns**:
- `bool`: True if the permission was revoked successfully, False otherwise.

**Raises**:
- `PluginSandboxError`: If the plugin is not registered.

#### `set_resource_limits(plugin_id: str, resource_limits: ResourceLimits) -> bool`

Set the resource limits for a plugin.

**Args**:
- `plugin_id`: The ID of the plugin.
- `resource_limits`: The resource limits to set.

**Returns**:
- `bool`: True if the resource limits were set successfully, False otherwise.

**Raises**:
- `PluginSandboxError`: If the plugin is not registered.

#### `add_allowed_module(plugin_id: str, module_name: str) -> bool`

Add a module to the list of modules a plugin is allowed to import.

**Args**:
- `plugin_id`: The ID of the plugin.
- `module_name`: The name of the module to allow.

**Returns**:
- `bool`: True if the module was added successfully, False otherwise.

**Raises**:
- `PluginSandboxError`: If the plugin is not registered.

#### `remove_allowed_module(plugin_id: str, module_name: str) -> bool`

Remove a module from the list of modules a plugin is allowed to import.

**Args**:
- `plugin_id`: The ID of the plugin.
- `module_name`: The name of the module to disallow.

**Returns**:
- `bool`: True if the module was removed successfully, False otherwise.

**Raises**:
- `PluginSandboxError`: If the plugin is not registered.

## Exceptions

### PermissionDeniedError

Exception raised when a plugin attempts to perform an action without permission.

```python
class PermissionDeniedError(Exception):
    """Exception raised when a plugin attempts to perform an action without permission."""
    pass
```

### PluginSandboxError

Exception raised when there's an error in the plugin sandbox.

```python
class PluginSandboxError(Exception):
    """Exception raised when there's an error in the plugin sandbox."""
    pass
```

## Usage Examples

### Creating a Sandbox Manager

```python
from src.plugins.plugin_sandbox import PluginSandboxManager

# Create a sandbox manager
manager = PluginSandboxManager()
```

### Registering a Plugin

```python
from src.plugins.plugin_sandbox import (
    PluginSandboxManager, PluginPermission, ResourceLimits,
    PERMISSION_FILE_READ, PERMISSION_FILE_WRITE
)

# Create a sandbox manager
manager = PluginSandboxManager()

# Register a plugin with permissions
manager.register_plugin(
    "my-plugin",
    permissions={PERMISSION_FILE_READ, PERMISSION_FILE_WRITE},
    resource_limits=ResourceLimits(
        max_memory_mb=200,
        max_cpu_time_sec=20,
        max_file_handles=20,
        max_network_connections=10
    ),
    allowed_modules={"os", "sys", "math"}
)
```

### Loading and Activating a Plugin

```python
from src.plugins.plugin_sandbox import PluginSandboxManager

# Create a sandbox manager
manager = PluginSandboxManager()

# Register a plugin
manager.register_plugin("my-plugin")

# Load the plugin
plugin = manager.load_plugin("my-plugin", "/path/to/my-plugin.py")

# Activate the plugin
manager.activate_plugin("my-plugin")
```

### Deactivating and Unloading a Plugin

```python
from src.plugins.plugin_sandbox import PluginSandboxManager

# Create a sandbox manager
manager = PluginSandboxManager()

# Register and load a plugin
manager.register_plugin("my-plugin")
manager.load_plugin("my-plugin", "/path/to/my-plugin.py")
manager.activate_plugin("my-plugin")

# Deactivate the plugin
manager.deactivate_plugin("my-plugin")

# Unload the plugin
manager.unload_plugin("my-plugin")
```

### Managing Permissions

```python
from src.plugins.plugin_sandbox import (
    PluginSandboxManager, PERMISSION_FILE_READ, PERMISSION_NETWORK
)

# Create a sandbox manager
manager = PluginSandboxManager()

# Register a plugin with read permission
manager.register_plugin("my-plugin", permissions={PERMISSION_FILE_READ})

# Grant network permission
manager.grant_permission("my-plugin", PERMISSION_NETWORK)

# Revoke read permission
manager.revoke_permission("my-plugin", PERMISSION_FILE_READ)
```

### Managing Resource Limits

```python
from src.plugins.plugin_sandbox import PluginSandboxManager, ResourceLimits

# Create a sandbox manager
manager = PluginSandboxManager()

# Register a plugin
manager.register_plugin("my-plugin")

# Set resource limits
manager.set_resource_limits(
    "my-plugin",
    ResourceLimits(
        max_memory_mb=200,
        max_cpu_time_sec=20,
        max_file_handles=20,
        max_network_connections=10
    )
)
```

### Managing Allowed Modules

```python
from src.plugins.plugin_sandbox import PluginSandboxManager

# Create a sandbox manager
manager = PluginSandboxManager()

# Register a plugin
manager.register_plugin("my-plugin")

# Add allowed modules
manager.add_allowed_module("my-plugin", "os")
manager.add_allowed_module("my-plugin", "sys")

# Remove allowed module
manager.remove_allowed_module("my-plugin", "os")
```

## Best Practices

1. **Principle of Least Privilege**: Grant plugins only the permissions they need to function. Avoid granting unnecessary permissions, especially powerful ones like `PERMISSION_PROCESS` or `PERMISSION_SYSTEM`.

2. **Resource Limits**: Set appropriate resource limits for plugins to prevent them from consuming too many system resources. Consider the plugin's requirements and adjust limits accordingly.

3. **Module Restrictions**: Only allow plugins to import modules they need. Be cautious with modules that provide access to system resources or sensitive information.

4. **Error Handling**: Handle exceptions from the plugin sandbox system gracefully. Provide clear error messages to users when a plugin fails to load or activate.

5. **Plugin Isolation**: Keep plugins isolated from each other and the main application. Avoid sharing sensitive data or resources between plugins.

6. **Regular Auditing**: Regularly audit plugins and their permissions to ensure they are not requesting or using more permissions than necessary.

7. **User Consent**: Inform users about the permissions a plugin requires and get their consent before installing or activating a plugin.

8. **Secure Loading**: Load plugins from trusted sources only. Consider implementing code signing or other verification mechanisms to ensure plugin integrity.

9. **Monitoring**: Monitor plugin behavior at runtime to detect and prevent malicious activities. Consider implementing a plugin reputation system.

10. **Documentation**: Provide clear documentation for plugin developers on how to request and use permissions, and how to work within the sandbox environment.
