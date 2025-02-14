"""
File Location: main.py
Author: Lizza Celestia
Version: ALizz_AI_V0_9
Created Date: 2025-02-12
Modified Date: 2025-02-14
Description:

"""

import time
import asyncio
from core.core import Core
from core.logging_setup import setup_logging
import logging

async def main():
    # Set up logging at DEBUG/INFO level, optionally specifying a file
    setup_logging(log_level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("ALizz Booting up...")

    # Initialize the core with the plugins folder path
    core = Core(plugin_directory="plugins")
    # Start the system
    core.boot()
    logger.debug(f"Loaded Plugin successfully: {core.plugin_manager.loaded_plugins}")
    
    try:
        # Manual commands
        while True:
            print("System is running. Type 'exit' to shut down...")
            cmd = input("Enter a command (exit/reload/...) > ").strip().lower()

            if cmd == "exit":
                break

            elif cmd == "reload":
                print(f"Available plugins:")
                for plugin_name in core.plugin_manager.loaded_plugins:
                    print(f"> {plugin_name}")

                plugin_name = input("Enter a module name to reload: ").strip().lower()
                if plugin_name in core.plugin_manager.loaded_plugins:
                    logger.info(f"'Manually Reloading plugin {plugin_name}'...")
                    core.plugin_manager.reload_plugin(plugin_name)
                else:
                    print(f"No Plugin named:'{plugin_name}'")
            
            elif cmd == "send":
                print(f"Available Subscribers:")
                for subscription_name in core.event_bus._subscribers:
                    print(f"> {subscription_name}")
                publish_cmd = input("what to publish (ex. START_DISCORD): ").strip().upper()
                publish_data = input("Message to TTS: ").strip()
                logger.info(f"'Manually publishing {publish_cmd} event with data: {publish_data}'")
                core.event_bus.publish(
                    f"{publish_cmd}",
                    {"content": f"{publish_data}"}
                    )
                
            elif cmd == "restart":
                core.boot()
                logger.info(f"'Rebooting plugin list'")
            
            else:
                logger.warning("Unknown command. Available: exit, reload, send, restart")

            time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("TERMINATING ======================")
        logger.info("Shutting down...")
        core.shutdown()
        logger.info("System shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
