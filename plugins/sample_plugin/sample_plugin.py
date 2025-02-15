"""
File Location: main.py
Author: Lizza Celestia
Version: ALizz_AI_V0_9
Created Date: 2025-02-12
Modified Date: 2025-02-14
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

# manually updated list of published event for this plungin  
publishing_list={"READY_SAMPLE": "bool: {sel.bool}",
                 "SAMPLE_RESULTS": "content: {self.result}",
                 }
# how to log and publish an Event
# logger.debug(f"[{plugin_name}] Publishing 'READY_SAMPLE' event.")
# self.core.event_bus.publish(f"READY_SAMPLE",{"bool": self.bool})

subscriptions_list = {
                        "TERMINATE_PLUGINS": "handle_terminate_event",
                        "STOP_SAMPLE": "handle_stop_event",
                        "START_SAMPLE": "handle_start_event",
                        }

plugin_name = "Sample"


class SamplePlugin(BasePlugin):
#####################################################
#                  Initialize
#####################################################
    def __init__(self, core, enabled=True):
        self.core = core        # enables the event_bus
        self.enabled = enabled
        self.running = False
        # Subscribe to an event (e.g., "PLUGIN_STARTED")
        for event, handler in subscriptions_list.items():
            self.core.event_bus.subscribe(event, getattr(self, handler))
            logger.debug(f"[{plugin_name}] Subscribed to '{event}' with handler '{handler}'.")
            
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
        if self.count < 10:
            for count in range(10):
                logger.info(f"[{plugin_name}] {self.count} sample data is running...")
                self.count = count
            self.count += 1
        logger.info(f"[{plugin_name}] is running sample: {self.running}")

#####################################################
#                  Event Functions
#####################################################
    async def handle_start_event(self, data):
        # self.running = data["content"]
        self.running = True
        self.count = 0
        await self.run()

    async def handle_stop_event(self, data):
        # self.running = data["content"]
        self.running = False
        self.count = 0
        await self.run()

    async def handle_terminate_event(self, data):
        self.enabled = False
