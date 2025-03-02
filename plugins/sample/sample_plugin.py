"""
File Location: plugins/sample/sample_plugin.py
Author: Lizza Celestia
Version: ALizz_AI_V1_0
Created Date: 2025-02-12
Modified Date: 2025-03-02
Description:

"""
# sample_plugin.py
from core.base_plugin import BasePlugin
import asyncio
import logging
import os
if os.path.exists("constants.py"):
    from constants import *
else:
    # Define local constants
    PATH_const      = "place_holder"

logger = logging.getLogger(__name__)

# manually update list of published event for this plungin  
publishing_list={
                    "PLUGIN_STATUS_SAMPLE": "bool: {bool}",
                 }
# how to log and publish an Event
# logger.debug(f"[{plugin_name}] Publishing 'PLUGIN_STATUS_SAMPLE' event.")
# self.core.event_bus.publish(f"PLUGIN_STATUS_SAMPLE",{"bool": self.bool})

plugin_name = "Sample"

class SamplePlugin(BasePlugin):
#####################################################
#                  Initialize
#####################################################
    def __init__(self, core):
        self.core = core        # enables the event_bus
        self.status = False
        self.loop = None  # Store the loop reference
        self.stop_event = asyncio.Event()  # Async event to signal stopping

        # subscription list for the plugin and used for unsubscribing by the plugin manager
        self.subscriptions_list = { 
                                    "PLUGIN_STOP_sample"    : "handle_stop_event",          # PLUGIN_STOP_{plugin folder name}
                                    "STATUS_CHECK"          : "handle_status_check_event",
                                    }

        # Subscribe to the event in subscriptions_list
        for event, handler in self.subscriptions_list.items():
            self.core.event_bus.subscribe(event, getattr(self, handler))
            logger.info(f"[{plugin_name}] Subscribed to '{event}' with handler '{handler}'.")
            
        # self.variables
        self.count = 0 # for testing sample plugin

#####################################################
#                  Tread loop
#####################################################
    def init_event_loop(self):
        """Creates and runs a new event loop inside a thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.run())  # Start main async function

        except asyncio.CancelledError:
            logger.warning(f"[{plugin_name}] Event loop cancelled. Exiting thread safely.")

        finally:
            self.status = False
            logger.debug(f"[{plugin_name}] Publishing 'PLUGIN_STATUS_SAMPLE' event: {self.status}")
            self.core.event_bus.publish("PLUGIN_STATUS_SAMPLE", {"bool": self.status})

            if not self.loop.is_closed():
                self.loop.close()  # Ensure loop is properly closed
            logger.info(f"[{plugin_name}] Event loop closed.")

#####################################################
#                  Main loop
#####################################################
    async def run(self):
        logger.info(f"[{plugin_name}] is running...")
        self.status = True
        logger.debug(f"[{plugin_name}] Publishing 'PLUGIN_STATUS_SAMPLE' event.")
        self.core.event_bus.publish("PLUGIN_STATUS_SAMPLE",{"bool": self.status})

        while not self.stop_event.is_set():
            if self.stop_event.is_set():  # Check immediately if stop was requested
                break
            if self.count < 10:
                for count in range(10):
                    logger.info(f"[{plugin_name}] {self.count} sample data is running...")
                    self.count = count + 1
            logger.info(f"[{plugin_name}] is running sample.")
            await asyncio.sleep(5)  # Simulate async work


    #####################################################
    #                  Additional Functions
    #####################################################    

    
#####################################################
#                  Subscription Event Handlers
#####################################################
# ================== Required Subs by the core ==================
    async def handle_stop_event(self, data):
        """Stops all processing before unloading."""
        logger.info(f"[{plugin_name}] Received STOP event.")

        self.stop_event.set()  # Signal any manual stop conditions

        logger.info(f"[{plugin_name}] plugin successfully stopped.")

    async def handle_status_check_event(self, data):
        try:
            logger.debug(f"[{plugin_name}] Asked for Status check.")
            logger.debug(f"[{plugin_name}] Publishing 'PLUGIN_STATUS_SAMPLE' event. {self.status}")
            self.core.event_bus.publish("PLUGIN_STATUS_SAMPLE",{"bool": self.status})

        except Exception as e:
            logger.error(f"[{plugin_name}] Error: {e}")

# ================== additional Subs ==================


