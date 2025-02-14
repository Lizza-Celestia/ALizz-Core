"""
File Location: core/base_plugin.py
Author: Lizza Celestia
Version: ALizz_AI_V0_9
Create Date: 2025-02-12
Modified Date: 2025-02-14
Description:
"""
from abc import ABC
import asyncio

class BasePlugin(ABC):
#####################################################
#                  Initialize
#####################################################
    def __init__(self, signals, enabled=True):
        self.signals = signals
        self.enabled = enabled

#####################################################
#                  Tread loop
#####################################################
    def init_event_loop(self):
        asyncio.run(self.run())

#####################################################
#                  Run sequence
#####################################################
    async def run(self):
        pass

#####################################################
#                  Additional Functions
#####################################################

