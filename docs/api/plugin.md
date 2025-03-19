# RebelDESK Plugin API Reference

This document provides a reference for the RebelDESK Plugin API. It covers the classes and functions that you can use to create plugins for RebelDESK.

## Table of Contents

1. [Introduction](#introduction)
2. [Plugin Base Class](#plugin-base-class)
3. [Plugin Manager](#plugin-manager)
4. [Plugin Hooks](#plugin-hooks)
5. [Plugin Configuration](#plugin-configuration)
6. [Plugin Dependencies](#plugin-dependencies)
7. [Plugin Examples](#plugin-examples)

## Introduction

The RebelDESK Plugin API allows you to extend the functionality of RebelDESK by creating plugins. Plugins can add new features, modify existing features, or integrate with other tools and services.

## Plugin Base Class

All plugins must inherit from the `Plugin` base class defined in the `rebeldesk.plugins.plugin` module.

### `Plugin`

The plugin base class.

```python
from rebeldesk.plugins.plugin import Plugin

class MyPlugin(Plugin):
    def __init__(self):
        super().__init__()
        # Initialize your plugin
        
    def activate(self):
        # Activate your plugin
        
    def deactivate(self):
        # Deactivate your plugin
```

#### Methods

- `__init__()`: Initialize the plugin. You should call the parent class's `__init__` method and then initialize your plugin.
- `activate()`: Activate the plugin. This method is called when the plugin is activated. You should set up any hooks, UI elements, or other resources here.
- `deactivate()`: Deactivate the plugin. This method is called when the plugin is deactivated. You should clean up any resources here.
- `get_name()`: Get the plugin name. By default, this returns the class name. You can override this method to return a custom name.
- `get_version()`: Get the plugin version. By default, this returns "0.1.0". You can override this method to return a custom version.
- `get_description()`: Get the plugin description. By default, this returns an empty string. You can override this method to return a custom description.
- `get_author()`: Get the plugin author. By default, this returns an empty string. You can override this method to return a custom author.
- `get_dependencies()`: Get the plugin dependencies. By default, this returns an empty list. You can override this method to return a list of plugin IDs that your plugin depends on.

## Plugin Manager

The `PluginManager` class is responsible for loading, unloading, activating, and deactivating plugins. It is defined in the `rebeldesk.plugins.plugin_manager` module.

### `PluginManager`

The plugin manager class.

```python
from rebeldesk.plugins.plugin_manager import PluginManager

# Get the plugin manager
plugin_manager = PluginManager.instance()

# Load a plugin
plugin_manager.load_plugin("my_plugin")

# Activate a plugin
plugin_manager.activate_plugin("my_plugin")

# Deactivate a plugin
plugin_manager.deactivate_plugin("my_plugin")

# Unload a plugin
plugin_manager.unload_plugin("my_plugin")
```

#### Methods

- `instance()`: Get the singleton instance of the plugin manager.
- `load_plugin(plugin_id)`: Load a plugin by ID. Returns `True` if the plugin was loaded successfully, `False` otherwise.
- `unload_plugin(plugin_id)`: Unload a plugin by ID. Returns `True` if the plugin was unloaded successfully, `False` otherwise.
- `get_plugin(plugin_id)`: Get a plugin by ID. Returns the plugin instance or `None` if the plugin is not loaded.
- `get_plugins()`: Get all loaded plugins. Returns a dictionary mapping plugin IDs to plugin instances.
- `get_active_plugins()`: Get all active plugins. Returns a dictionary mapping plugin IDs to plugin instances.
- `is_plugin_active(plugin_id)`: Check if a plugin is active. Returns `True` if the plugin is active, `False` otherwise.
- `activate_plugin(plugin_id)`: Activate a plugin by ID. Returns `True` if the plugin was activated successfully, `False` otherwise.
- `deactivate_plugin(plugin_id)`: Deactivate a plugin by ID. Returns `True` if the plugin was deactivated successfully, `False` otherwise.

## Plugin Hooks

Hooks allow plugins to respond to events in the application. The `HookManager` class is responsible for registering and calling hooks. It is defined in the `rebeldesk.plugins.hook_manager` module.

### `HookManager`

The hook manager class.

```python
from rebeldesk.plugins.hook_manager import HookManager

# Get the hook manager
hook_manager = HookManager.instance()

# Register a hook
hook_manager.register_hook("file_opened", my_callback)

# Call a hook
hook_manager.call_hook("file_opened", file_path="path/to/file.py")

# Unregister a hook
hook_manager.unregister_hook("file_opened", my_callback)
```

#### Methods

- `instance()`: Get the singleton instance of the hook manager.
- `register_hook(hook_name, callback)`: Register a callback for a hook. The callback will be called when the hook is called.
- `unregister_hook(hook_name, callback)`: Unregister a callback for a hook.
- `call_hook(hook_name, **kwargs)`: Call a hook with the given arguments. All registered callbacks for the hook will be called with the arguments.

### Available Hooks

The following hooks are available in RebelDESK:

- `application_started`: Called when the application has started.
- `application_stopping`: Called when the application is about to stop.
- `file_opened`: Called when a file is opened. Arguments: `file_path`.
- `file_saved`: Called when a file is saved. Arguments: `file_path`.
- `file_closed`: Called when a file is closed. Arguments: `file_path`.
- `editor_created`: Called when an editor is created. Arguments: `editor`.
- `editor_destroyed`: Called when an editor is destroyed. Arguments: `editor`.
- `editor_text_changed`: Called when the text in an editor changes. Arguments: `editor`.
- `editor_language_changed`: Called when the language of an editor changes. Arguments: `editor`, `language`.
- `editor_theme_changed`: Called when the theme of an editor changes. Arguments: `editor`, `theme`.
- `plugin_loaded`: Called when a plugin is loaded. Arguments: `plugin_id`, `plugin`.
- `plugin_unloaded`: Called when a plugin is unloaded. Arguments: `plugin_id`.
- `plugin_activated`: Called when a plugin is activated. Arguments: `plugin_id`, `plugin`.
- `plugin_deactivated`: Called when a plugin is deactivated. Arguments: `plugin_id`, `plugin`.

## Plugin Configuration

Plugins can have configuration options that can be set by the user. The `PluginConfig` class is responsible for managing plugin configuration. It is defined in the `rebeldesk.plugins.plugin_config` module.

### `PluginConfig`

The plugin configuration class.

```python
from rebeldesk.plugins.plugin_config import PluginConfig

# Get the plugin configuration
config = PluginConfig.instance()

# Get a configuration value
value = config.get("my_plugin", "option_name", default_value)

# Set a configuration value
config.set("my_plugin", "option_name", value)

# Remove a configuration value
config.remove("my_plugin", "option_name")

# Clear all configuration values for a plugin
config.clear("my_plugin")
```

#### Methods

- `instance()`: Get the singleton instance of the plugin configuration.
- `get(plugin_id, key, default=None)`: Get a configuration value for a plugin. Returns the value or `default` if the value is not set.
- `set(plugin_id, key, value)`: Set a configuration value for a plugin.
- `remove(plugin_id, key)`: Remove a configuration value for a plugin.
- `clear(plugin_id)`: Clear all configuration values for a plugin.
- `contains(plugin_id, key)`: Check if a configuration value exists for a plugin. Returns `True` if the value exists, `False` otherwise.
- `sync()`: Sync configuration values to disk.

## Plugin Dependencies

Plugins can depend on other plugins. The `PluginDependencyResolver` class is responsible for resolving plugin dependencies. It is defined in the `rebeldesk.plugins.plugin_dependency_resolver` module.

### `PluginDependencyResolver`

The plugin dependency resolver class.

```python
from rebeldesk.plugins.plugin_dependency_resolver import PluginDependencyResolver

# Create a dependency resolver
resolver = PluginDependencyResolver()

# Resolve dependencies for a plugin
dependencies = resolver.resolve_dependencies("my_plugin")

# Check if a plugin's dependencies are satisfied
is_satisfied = resolver.are_dependencies_satisfied("my_plugin")
```

#### Methods

- `resolve_dependencies(plugin_id)`: Resolve dependencies for a plugin. Returns a list of plugin IDs that the plugin depends on, in the order they should be loaded.
- `are_dependencies_satisfied(plugin_id)`: Check if a plugin's dependencies are satisfied. Returns `True` if all dependencies are loaded and active, `False` otherwise.

## Plugin Examples

Here are some examples of plugins for RebelDESK:

### Simple Plugin

```python
from rebeldesk.plugins.plugin import Plugin

class HelloWorldPlugin(Plugin):
    def __init__(self):
        super().__init__()
        
    def get_name(self):
        return "Hello World"
        
    def get_version(self):
        return "1.0.0"
        
    def get_description(self):
        return "A simple Hello World plugin"
        
    def get_author(self):
        return "RebelDESK Team"
        
    def activate(self):
        print("Hello, World!")
        
    def deactivate(self):
        print("Goodbye, World!")
```

### Plugin with Hooks

```python
from rebeldesk.plugins.plugin import Plugin
from rebeldesk.plugins.hook_manager import HookManager

class FileLoggerPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.hook_manager = HookManager.instance()
        
    def get_name(self):
        return "File Logger"
        
    def get_version(self):
        return "1.0.0"
        
    def get_description(self):
        return "Logs file operations"
        
    def get_author(self):
        return "RebelDESK Team"
        
    def activate(self):
        self.hook_manager.register_hook("file_opened", self.on_file_opened)
        self.hook_manager.register_hook("file_saved", self.on_file_saved)
        self.hook_manager.register_hook("file_closed", self.on_file_closed)
        
    def deactivate(self):
        self.hook_manager.unregister_hook("file_opened", self.on_file_opened)
        self.hook_manager.unregister_hook("file_saved", self.on_file_saved)
        self.hook_manager.unregister_hook("file_closed", self.on_file_closed)
        
    def on_file_opened(self, file_path):
        print(f"File opened: {file_path}")
        
    def on_file_saved(self, file_path):
        print(f"File saved: {file_path}")
        
    def on_file_closed(self, file_path):
        print(f"File closed: {file_path}")
```

### Plugin with Configuration

```python
from rebeldesk.plugins.plugin import Plugin
from rebeldesk.plugins.plugin_config import PluginConfig

class ConfigurablePlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.config = PluginConfig.instance()
        
    def get_name(self):
        return "Configurable Plugin"
        
    def get_version(self):
        return "1.0.0"
        
    def get_description(self):
        return "A plugin with configuration options"
        
    def get_author(self):
        return "RebelDESK Team"
        
    def activate(self):
        # Get configuration values
        self.option1 = self.config.get("configurable_plugin", "option1", "default1")
        self.option2 = self.config.get("configurable_plugin", "option2", "default2")
        
        print(f"Option 1: {self.option1}")
        print(f"Option 2: {self.option2}")
        
    def deactivate(self):
        # Save configuration values
        self.config.set("configurable_plugin", "option1", self.option1)
        self.config.set("configurable_plugin", "option2", self.option2)
        self.config.sync()
```

### Plugin with Dependencies

```python
from rebeldesk.plugins.plugin import Plugin

class DependentPlugin(Plugin):
    def __init__(self):
        super().__init__()
        
    def get_name(self):
        return "Dependent Plugin"
        
    def get_version(self):
        return "1.0.0"
        
    def get_description(self):
        return "A plugin that depends on other plugins"
        
    def get_author(self):
        return "RebelDESK Team"
        
    def get_dependencies(self):
        return ["hello_world", "file_logger"]
        
    def activate(self):
        print("Dependent plugin activated")
        
    def deactivate(self):
        print("Dependent plugin deactivated")
