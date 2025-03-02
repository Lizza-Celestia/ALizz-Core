"""
File Location: core/plugin_manager.py
Author: Lizza Celestia
Version: ALizz_AI_V1_0
Create Date: 2025-02-12
Modified Date: 2025-03-02
Description:
"""
# core/plugin_manager.py
import importlib
import sys
import time
import threading
import asyncio
from pathlib import Path
from typing import Dict
from core.base_plugin import BasePlugin

import logging
logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self, plugin_directory: str, core=None, priority_plugins=[]):
        self.plugin_directory = Path(plugin_directory)
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        self.core = core  # <-- must be set. acces for the event_bus which will be send to each plugin on init
        self.module_threads = {}
        self.priority_plugins = priority_plugins

    def priority_loading(self):
        logger.debug(f"[PluginManager]: Scanning directory: {self.plugin_directory}")
        for item in self.plugin_directory.iterdir():
            try:
                if item.name in self.priority_plugins:
                    logger.debug(f"Checking: {item} (Is dir? {item.is_dir()})")
                    if item.is_dir() and (item / "__init__.py").exists():
                        logger.debug(f"Found priority plugin candidate: {item.name}")
                        self._load_plugin(item.name)
                    else:
                        logger.error(f"Priority Plugin: {item.name} (not a plugin or missing __init__.py)")
                else:
                    logger.debug(f"Skipping: {item.name} (not in priority list) {self.priority_plugins}")
            
            except Exception as e:
                logging.error(f"'Error discovering' plugin '{item}': {e}")


    def discover_plugins(self):
        """
        Scan the plugin folder and load active plugins, plugins with existing __init__.py
        """
        if not self.plugin_directory.exists():
            logger.error(f"[PluginManager] Plugin directory '{self.plugin_directory}' does not exist!")
            return
    # start by loading priority plugins first
        if self.priority_plugins:
            logger.debug(f"[PluginManager]: Scanning for priority plugins: {self.priority_plugins}")
            self.priority_loading()
        else:
            logger.debug(f"[PluginManager]: Priority list is empty, starting normal loading...")
            
    # load the rest of the plugins
        logger.debug(f"[PluginManager]: 'Scanning directory: {self.plugin_directory}'")
        for item in self.plugin_directory.iterdir():
            try:
                logger.debug(f"Checking: {item} (Is dir? {item.is_dir()})")

                if item.is_dir() and (item / "__init__.py").exists():       # check if the plugin is active
                    if item.name in self.loaded_plugins:                    # if the plugin is already loaded, ignore an go to next
                        logger.debug(f"[PluginManager] Plugin '{item.name}' is already loaded. Skipping.") 
                        continue
                    logger.info(f"[PluginManager] Found plugin candidate: '{item.name}'")      
                    self._load_plugin(item.name)
                    
                else:
                    logger.debug(f"[PluginManager] Skipping '{item.name}' (Not a plugin or missing __init__.py)")
            except Exception as e:
                logging.error(f"'Error discovering' plugin '{item}': {e}")

    def rediscover_plugins(self):
        """
        Rescan the plugin folder and load new active plugins and unload deactivate plugins
        """
        logger.debug(f"[PluginManager]: Scanning directory: {self.plugin_directory}")
        for item in self.plugin_directory.iterdir():
            try:
                logger.debug(f"Checking: {item} (Is dir? {item.is_dir()})")
                if item.is_dir() and (item / "__init__.py").exists():       # check if the plugin is active
                    if item.name in self.loaded_plugins:                    # if the plugin is already loaded, ignore an go to next
                        logger.debug(f"Plugin '{item.name}' is already loaded") 
                        continue
                    logger.debug(f"Loading newly activated plugin: '{item.name}'")        
                    self._load_plugin(item.name)

                elif item.is_dir() and not (item / "__init__.py").exists(): # if the plugin is inactive
                    if item.name in self.loaded_plugins:                    # check if the plugin was loaded
                        logger.debug(f"Unloading deactivated plugin: '{item.name}'")
                        self.unload_plugin(item.name)                       # if so unloaded
                else:
                    logger.debug(f"Skipping '{item.name}' (not a plugin)")
                        
            except Exception as e:
                logging.error(f"'Error discovering' plugin '{item}': {e}")


    def _load_plugin(self, plugin_name: str):
        """
        Dynamically loads a plugin based on naming conventions:
        - The plugin’s code is in plugins/<plugin_name>/<plugin_name>_plugin.py
        - The main plugin class is <PluginName>Plugin, e.g. "EchoPlugin" for "echo".
        - start a thread for the plugin 
        """
        try:
            module_path = f"plugins.{plugin_name}.{plugin_name}_plugin"
            logger.debug(f"'Loading' plugin module: {module_path}")
        # Step 1: Import the plugin module dynamically
            module = importlib.import_module(module_path)
            logger.debug(f"[PluginManager] Module '{module_path}' imported successfully.")

        # Step 2: Construct the expected plugin class name based on the plugin folder name
            class_name = f"{plugin_name.capitalize()}Plugin"
            if not hasattr(module, class_name):
                logger.error(f"[PluginManager] Plugin class '{class_name}' not found in module '{module_path}'.")
                return
            plugin_class = getattr(module, class_name)
            logger.debug(f"[PluginManager] Found plugin class '{class_name}'.")
            
        # Step 3: Instantiate the plugin
            plugin_instance = plugin_class(self.core)
            if not isinstance(plugin_instance, BasePlugin):
                logger.warning(f"[PluginManager] Plugin '{plugin_name}' does not implement BasePlugin. Skipping.")
                return
            
            self.loaded_plugins[plugin_name] = plugin_instance
            logger.info(f"[PluginManager] Plugin '{plugin_name}' loaded successfully.")

        # Step 4: Start the plugin in a separate thread
            logger.debug(f"[PluginManager] Initializing plugin event loop for '{plugin_name}'...")
            module_thread = threading.Thread(target=plugin_instance.init_event_loop, name=f"Thread-{plugin_name}")
            self.module_threads[plugin_name] = module_thread
            module_thread.start()
            logger.info(f"[PluginManager] Plugin '{plugin_name}' thread started successfully.")

        except Exception as e:
            logger.error(f"'Failed to load' plugin {plugin_name}: {e}", exc_info=True)

    def reload_plugin(self, plugin_name: str):
        """
        Reloads a plugin by unloading and then reloading it.
        Ensures proper cleanup before re-importing.
        """
        logger.info(f"[PluginManager] 'Reloading' plugin '{plugin_name}'...")

        self.print_active_threads()  # Debugging: Check active threads before reloading
    
        if plugin_name in self.loaded_plugins:
            try:
            # Step 1: Unload the existing plugin
                self.unload_plugin(plugin_name)

            # Step 2: Ensure the module is removed from sys.modules
                module_path = f"plugins.{plugin_name}.{plugin_name}_plugin"
                if module_path in sys.modules:
                    logger.debug(f"[PluginManager] Removing module '{module_path}' from sys.modules...")
                    del sys.modules[module_path]

            # Step 3: Wait briefly to allow cleanup
                time.sleep(1)

            # Step 4: Reload the plugin
                self._load_plugin(plugin_name)

                self.print_active_threads()  # Debugging: Check active threads before reloading
    
            except Exception as e:
                logging.error(f"'Error reloading' module {plugin_name}: {e}")
        else:
            logging.warning(f"Can't 'Reload' Plugin: '{plugin_name}', it is not in 'loaded_plugins'")

    def unload_plugin(self, plugin_name: str):
        """
        Unloads a plugin if it is loaded: stops the event loop,
        ensures the thread exits, and removes it from memory.
        """
        if plugin_name in self.loaded_plugins:
            try:
                logger.info(f"[PluginManager] Unloading plugin '{plugin_name}'...")

                plugin_instance = self.loaded_plugins[plugin_name]

            # Step 1: Send STOP event to plugin
                if hasattr(plugin_instance, "handle_stop_event"):
                    logger.debug(f"[{plugin_name}] Sending STOP signal before unloading...")
                    # asyncio.run(plugin_instance.handle_stop_event({}))
                    logger.debug(f"[{plugin_name}] Publishing 'PLUGIN_STOP_{plugin_name}' event.")
                    self.core.event_bus.publish(f"PLUGIN_STOP_{plugin_name}",{"bool": True})
                    plugin_instance.stop_event.set()

                time.sleep(0.5)  # Allow time for the plugin to stop

            # Step 2: Unsubscribe from all event handlers before unloading
                if hasattr(plugin_instance, "subscriptions_list"):
                    for event, handler in plugin_instance.subscriptions_list.items():
                        event_handler = getattr(plugin_instance, handler, None)
                        if event_handler:
                            self.core.event_bus.unsubscribe(event, event_handler)
                            
            # Step 3: Stop the plugin's event loop if it's running
                if plugin_instance.loop and plugin_instance.loop.is_running():
                    logger.debug(f"[PluginManager] Stopping event loop of {plugin_name}...")
                    plugin_instance.loop.call_soon_threadsafe(plugin_instance.loop.stop)

            # Step 4: Wait for the thread to exit properly
                module_thread = self.module_threads.get(plugin_name)
                if module_thread and module_thread.is_alive():
                    logger.debug(f"[PluginManager] Waiting for {plugin_name} thread to terminate...")
                    module_thread.join(timeout=10)  # Give the thread time to exit
                    if module_thread.is_alive():
                        logger.warning(f"[PluginManager] Warning: {plugin_name} Thread did not terminate properly!")

            # Step 5: Remove the plugin from internal dictionaries
                del self.loaded_plugins[plugin_name]
                del self.module_threads[plugin_name]

            # Step 6: Remove the module from sys.modules
                module_path = f"plugins.{plugin_name}.{plugin_name}_plugin"
                if module_path in sys.modules:
                    logger.debug(f"[PluginManager] Removing module {plugin_name} from sys.modules...")
                    del sys.modules[module_path]

                logger.info(f"[PluginManager] Plugin '{plugin_name}' unloaded successfully.")
                
            except Exception as e:
                logging.error(f"'Error unloading' module {plugin_name}: {e}")
        else:
            logging.warning(f"Can't 'Unload' Plugin: '{plugin_name}', it is not in 'loaded_plugins")

    def print_active_threads(self):
        """Prints all currently active threads in the application."""
        logger.info("=== Active Threads ===")
        for thread in threading.enumerate():
            logger.info(f"Thread Name: {thread.name}, Alive: {thread.is_alive()}, Daemon: {thread.daemon}")
        logger.info("======================")
