"""
File Location: core/plugin_manager.py
Author: Lizza Celestia
Version: ALizz_AI_V0_9
Create Date: 2025-02-12
Modified Date: 2025-02-19
Description:
"""
# core/plugin_manager.py
import importlib
import sys
import threading
from pathlib import Path
from typing import Dict
from core.base_plugin import BasePlugin

import logging
logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self, plugin_directory: str, core=None):
        self.plugin_directory = Path(plugin_directory)
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        self.core = core  # <-- must be set. acces for the event_bus which will be send to each plugin on init
        self.module_threads = {}

    def discover_plugins(self):
        """
        Scan the plugin folder and load active plugins, plugins with existing __init__.py
        """
        logger.debug(f"PluginManager: Scanning directory: {self.plugin_directory}")
        for item in self.plugin_directory.iterdir():
            try:
                logger.debug(f"Checking: {item} (Is dir? {item.is_dir()})")
                if item.is_dir() and (item / "__init__.py").exists():
                    logger.debug(f"Found plugin candidate: {item.name}")
                    self._load_plugin(item.name)
                else:
                    logger.debug(f"Skipping {item.name} (not a plugin or missing __init__.py)")
            except Exception as e:
                logging.error(f"'Error discovering' plugin '{item}': {e}")

    def rediscover_plugins(self):
        """
        Rescan the plugin folder and load new active plugins and unload deactivate plugins
        """
        logger.debug(f"PluginManager: Scanning directory: {self.plugin_directory}")
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
            module = importlib.import_module(module_path)
            
            # Construct the plugin class name based on the plugin folder name
            class_name = f"{plugin_name.capitalize()}Plugin"
            plugin_class = getattr(module, class_name)
            
            # Instantiate the plugin
            plugin_instance = plugin_class(self.core)
            if isinstance(plugin_instance, BasePlugin):
                self.loaded_plugins[plugin_name] = plugin_instance

                # Initialize and start every discovered plugin in a thread
                logger.debug(f"Initializing plugin 'thread' for '{plugin_name}'...")
                module_thread = threading.Thread(target=plugin_instance.init_event_loop, daemon=True)
                logger.debug(f"Thread'{module_thread}'.")
                self.module_threads[plugin_name] = module_thread
                module_thread.start()
                logger.info(f"Plugin '{plugin_name}' 'loaded' successfully.")
                
            else:
                logger.warning(f"Plugin {plugin_name} does not implement BasePlugin.")
        except Exception as e:
            logger.error(f"'Failed to load' plugin {plugin_name}: {e}", exc_info=True)

    def reload_plugin(self, plugin_name: str):
        """
        Reloads a plugin by unloading and then reloading. 
        Removes the module from sys.modules to force a fresh import.
        """
        logger.info(f"'Reloading' plugin '{plugin_name}'...")
        if plugin_name in self.loaded_plugins:
            try:
                self.unload_plugin(plugin_name)
                module_path = f"plugins.{plugin_name}.{plugin_name}_plugin"
                if module_path in sys.modules:
                    del sys.modules[module_path]
                self._load_plugin(plugin_name)

            except Exception as e:
                logging.error(f"'Error reloading' module {plugin_name}: {e}")
        else:
            logging.warning(f"Can't 'Reload' Plugin: '{plugin_name}', it is not in 'loaded_plugins'")

    def unload_plugin(self, plugin_name: str):
        """
        Unloads a plugin if it is loaded: join the thread,
        then removes it from the loaded_plugins dictionary.
        """
        if plugin_name in self.loaded_plugins:
            try:
                logger.debug(f"[{plugin_name}] Publishing 'STOP_{plugin_name}' event.")
                self.core.event_bus.publish(f"STOP_{plugin_name}",{"bool": True})

                module_thread = self.module_threads[plugin_name]
                if module_thread and module_thread.is_alive():
                    logger.debug(f"'{plugin_name}' Thread to join: '{module_thread}'.")
                    module_thread.join()
                    logger.debug(f"Plugin '{plugin_name}' thread 'joined'.")
                    del self.loaded_plugins[plugin_name]
                    logger.info(f"Plugin '{plugin_name}' 'unloaded'.")
                
            except Exception as e:
                logging.error(f"'Error unloading' module {plugin_name}: {e}")
        else:
            logging.warning(f"Can't 'Unload' Plugin: '{plugin_name}', it is not in 'loaded_plugins")
