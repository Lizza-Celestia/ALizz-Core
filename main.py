"""
File Location: main.py
Author: Lizza Celestia
Version: ALizz_AI_V0_9
Created Date: 2025-02-12
Modified Date: 2025-02-18
Description:

"""

import time
import asyncio
from core.core import Core
from core.logging_setup import setup_logging
import logging
import sys

async def main():
    # Set up logging at DEBUG/INFO/WARNING level, optionally specifying a file
    setup_logging(log_level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("ALizz Booting up...")

    # Initialize the core with the plugins folder path
    core = Core(plugin_directory="plugins")
    # Start the system
    core.boot()
    logger.debug(f"Loaded Plugin successfully: {core.plugin_manager.loaded_plugins}")
    logger.debug(f"Publishing 'READY_CORE' event.")
    core.event_bus.publish("READY_CORE",{"bool": True})
    try:
        # Manual commands
        cms_list = {"exit"      : "shut down core", 
                    "reload"    : "Reload an individual active plugin",
                    "send"      : "Publish an existing subscribed event",
                    "scan"      : "Scan for new actived/deactived plugins and load/unload them",
                    "restart"   : "Relaunch the core script",
                    }
        while True:
            print("System is running. Available commands:")
            for command, description in cms_list.items():
                print(f"> {command}: {description}")
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
                if publish_cmd in core.event_bus._subscribers:
                    types_msg = {"content","bool","user","time"}
                    for types in types_msg:
                        print(f"> {types}")
                    publish_Type = input("Message Type: ").strip()
                    if publish_Type in types_msg:
                        if publish_Type == "bool":
                            publish_data = input("bool: ").strip().capitalize()
                            if publish_data == "True": publish_data = True
                            elif publish_data == "False": publish_data = False
                            else: print(f"'{publish_Type}' is not a valid Boolean")

                        else:
                            publish_data = input("Message: ").strip().capitalize()
                        logger.info(f"'Manually publishing {publish_cmd} event with data: {publish_data}'")
                        core.event_bus.publish(publish_cmd,{publish_Type: publish_data})
                    else:
                        print(f"'{publish_Type}' is not a valid type")
                else:    
                    print(f"'{publish_cmd}' is not a subscribed event")

            elif cmd == "scan":
                logger.info(f"'Manual rescaning the plugin folder for new plugin'")
                core.plugin_manager.rediscover_plugins()

            elif cmd == "restart":
                logger.info(f"'Manual Full Reboot of plugin list'")
                core.shutdown()
                core.boot()
            
            else:
                logger.warning(f"'{cmd}' is an Unknown command. Available commands:")
                for command, description in cms_list.items():
                    print(f"> {command}: {description}")


            time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("TERMINATING ======================")
        logger.info("Shutting down...")
        core.shutdown()
        print("System shutdown complete.")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
