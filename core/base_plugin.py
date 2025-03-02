"""
File Location: core/base_plugin.py
Author: Lizza Celestia
Version: ALizz_AI_V1_0
Create Date: 2025-02-12
Modified Date: 2025-03-02
Description:
"""
from abc import ABC
import asyncio

class BasePlugin(ABC):
#####################################################
#                  Initialize
#####################################################
    def __init__(self, core):
        self.core = core
        self.status = False
        self.loop = None  # Store the loop reference
        self.stop_event = asyncio.Event()  # Async event to signal stopping
        self.subscriptions_list = {}  # Subscription list for the plugin
        
        # Subscribe to the event in subscriptions_list
        for event, handler in self.subscriptions_list.items():
            self.core.event_bus.subscribe(event, getattr(self, handler))
            
#####################################################
#                  Tread loop
#####################################################
    def init_event_loop(self):
        """Creates and runs a new event loop inside a thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self.run())  # Start main async function
        finally:
            self.status = False
            if not self.loop.is_closed():
                self.loop.close()  # Ensure loop is properly closed

#####################################################
#                  Run sequence
#####################################################
    async def run(self):
        pass

#####################################################
#                  Additional Functions
#####################################################

