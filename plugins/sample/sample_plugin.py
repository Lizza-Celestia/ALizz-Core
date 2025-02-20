"""
File Location: plugins/sample/sample_plugin.py
Author: Lizza Celestia
Version: ALizz_AI_V0_9
Created Date: 2025-02-12
Modified Date: 2025-02-20
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
    PATH_const      = "./plugins/sample/sample.txt"

logger = logging.getLogger(__name__)

# manually update list of published event for this plungin  
publishing_list={"PLUGIN_STATUS_SAMPLE": "bool: {bool}",
                #  "TTS_SPEAKING": "bool: {bool}",
                 }
# how to log and publish an Event
# logger.debug(f"[{plugin_name}] Publishing 'PLUGIN_STATUS_SAMPLE' event.")
# self.core.event_bus.publish(f"PLUGIN_STATUS_SAMPLE",{"bool": self.bool})

subscriptions_list = {  "TERMINATE_PLUGINS": "handle_terminate_event",
                        "STOP_sample": "handle_stop_sample_event",
                        # "START_SAMPLE": "handle_start_event",
                        }

plugin_name = "Sample"


class SamplePlugin(BasePlugin):
#####################################################
#                  Initialize
#####################################################
    def __init__(self, core):
        self.core = core        # enables the event_bus
        self.stop_event = asyncio.Event()  # Async event to signal stopping
        self.status = False

        # Subscribe to an event (e.g., "PLUGIN_STARTED")
        for event, handler in subscriptions_list.items():
            self.core.event_bus.subscribe(event, getattr(self, handler))
            logger.info(f"[{plugin_name}] Subscribed to '{event}' with handler '{handler}'.")
            
        self.count = 0 # for testing sample plugin

#####################################################
#                  Tread loop
#####################################################
# uncomment for plugins that require to be activated as the thread is created (ex. discord)
    # def init_event_loop(self):
    #     asyncio.run(self.run())

#####################################################
#                  Run sequence
#####################################################
    async def run(self):
        logger.info(f"[{plugin_name}] is running...")
        self.status = True
        logger.debug(f"[{plugin_name}] Publishing 'PLUGIN_STATUS_SAMPLE' event.")
        self.core.event_bus.publish("PLUGIN_STATUS_SAMPLE",{"bool": self.status})

        while not self.stop_event.is_set():
            if self.count < 10:
                for count in range(10):
                    logger.info(f"[{plugin_name}] {self.count} sample data is running...")
                    self.count = count + 1
            logger.info(f"[{plugin_name}] is running sample.")
            await asyncio.sleep(5)  # Simulate async work
            
        logger.debug(f"[{plugin_name}] event loop stopped.")
        self.status = False
        logger.debug(f"[{plugin_name}] Publishing 'PLUGIN_STATUS_SAMPLE' event.")
        self.core.event_bus.publish("PLUGIN_STATUS_SAMPLE",{"bool": self.status})


#####################################################
#                  Event Functions
#####################################################
    async def handle_terminate_event(self, data):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.call_soon_threadsafe(self.stop_event.set)  # Signal stop event in async loop

    async def handle_stop_sample_event(self, data):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.call_soon_threadsafe(self.stop_event.set)  # Signal stop event in async loop

    # async def handle_start_event(self, data):
        # self.running = data["content"]
        # self.count = 0
        # await self.run()

