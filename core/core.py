"""
File Location: core/core.py
Author: Lizza Celestia
Version: ALizz_AI_V0_9
Create Date: 2025-02-12
Modified Date: 2025-02-13
Description:
"""
# core/core.py

from core.plugin_manager import PluginManager
from core.event_bus import EventBus
import sys
import threading
import logging
logger = logging.getLogger(__name__)

# Path to the JSON file
plugin_setting_path = "settings_plugins.json"


class Core:
    """
    The core manages the system’s overall lifecycle and
    makes the event bus and plugin manager available to all plugins.
    """
    def __init__(self, plugin_directory: str):
        self.event_bus = EventBus()
        # Pass 'self' into the PluginManager so it can access the core/event bus
        self.plugin_manager = PluginManager(plugin_directory, core=self)
        self.module_threads = {}


    def boot(self):
        """
        Discover plugins, then initialize and start each one.
        """
        logger.info("Core booting up...")
        self.plugin_manager.discover_plugins()
        logger.info("All discovered plugins have been started.")

        logger.debug(f"Start 'Event bus' thread")
        try:
            event_thread = threading.Thread(target=self.event_bus.process_events, daemon=True)
            event_thread.start()
        except Exception as e:
            logger.error(f"Could not start the 'Event bus' thread. Error: {e}")

    def shutdown(self):
        """
        Gracefully stop and unload all plugins.
        """
        logger.debug("Publishing 'TERMINATE_PLUGINS' Event.")
        self.event_bus.publish(
            "TERMINATE_PLUGINS",
            {"message": False}
            )
        
        logger.info("Core, shutting down all plugins...")
        for plugin_name in list(self.plugin_manager.loaded_plugins.keys()):
            self.plugin_manager.unload_plugin(plugin_name)
        logger.info("All plugins unloaded. Shutdown complete.")

        logger.debug("Publishing 'TERMINATE' Event.")
        self.event_bus.publish(
            "TERMINATE",
            {"message": False}
            )
        
        sys.exit(0)








