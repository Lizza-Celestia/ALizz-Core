"""
File Location: core/event_bus.py
Author: Lizza Celestia
Version: ALizz_AI_V1_0
Create Date: 2025-02-13
Modified Date: 2025-03-02
Description:
"""
# import asyncio
from collections import defaultdict
import asyncio
import queue
import logging
logger = logging.getLogger(__name__)
plugin_name = "Event_bus"

class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)
        self.event_queue = queue.Queue()

    def subscribe(self, event_type: str, callback):
        """
        Subscribe a callback to a specific event type.
        :param event_type: The event type to listen for.
        :param callback: An async function to be called when the event is published.
        """
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data=None):
        """
        Publish an event to all subscribers of the event type.
        :param event_type: The event type.
        :param data: The data to pass to the subscribers.
        """               
        if event_type in self._subscribers:
            self.event_queue.put((event_type, data))

        elif event_type == "TERMINATE":
            self.event_queue.put((event_type, data))
            
        else:
            logger.warning(f"[{plugin_name}] There is NO subcription for Event: {event_type}, data:{data}")

    def unsubscribe(self, event_type: str, callback):
        """
        Unsubscribe a callback from a specific event type.
        :param event_type: The event type to stop listening for.
        :param callback: The function to remove from subscribers.
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                if not self._subscribers[event_type]:  # Remove the key if empty
                    del self._subscribers[event_type]
                logger.info(f"[{plugin_name}] Unsubscribed from '{event_type}'.")
            except ValueError:
                logger.warning(f"[{plugin_name}] Callback not found in '{event_type}' subscription list.")
        else:
            logger.warning(f"[{plugin_name}] Attempted to unsubscribe from non-existent event '{event_type}'.")


    def process_events(self):
        """Continuously process events in the queue (Run in a separate thread)"""
        while True:
            event_type, data = self.event_queue.get()
            if event_type == "TERMINATE":
                break  # Stop processing on terminate signal
            
            for callback in self._subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    # If the callback is async, run it in the event loop
                    asyncio.run(callback(data))
                else:
                    # If it's a normal function, just call it
                    callback(data)
