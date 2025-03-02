"""
File Location: main.py
Author: Lizza Celestia
Version: ALizz_AI_V1_0
Created Date: 2025-02-12
Modified Date: 2025-03-02
Description:

"""

import time
import asyncio
from core.core import Core
from core.logging_setup import setup_logging
import logging
import sys
import os

async def main():
    # Set up logging at DEBUG/INFO/WARNING level, optionally specifying a file
    setup_logging(log_level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("ALizz Booting up...")

    plugins_dir = "plugins"
    # Get the list of priority plugins (folders that start with "ctrl_")
    priority_plugins = [
                        folder for folder in os.listdir(plugins_dir)
                        if os.path.isdir(os.path.join(plugins_dir, folder)) and folder.startswith("ctrl_")
                        ]       

    logger.debug(f"priority CTRL plugins found: {priority_plugins}")

    core = Core(plugin_directory=plugins_dir, priority_plugins=priority_plugins)
    # Start the system
    core.boot()
    # logger.debug(f"Loaded Plugin successfully: {core.plugin_manager.loaded_plugins}")
    logger.debug(f"Publishing 'READY_CORE' event.")
    core.event_bus.publish("READY_CORE",{"bool": True})

    logger.info(f"'Manually publishing STATUS_CHECK event.'")
    core.event_bus.publish("STATUS_CHECK",{"bool": True})
    
    time.sleep(1)

    try:
        # Manual commands
        cms_list = {"exit"      : "shut down core script", 
                    "restart"   : "Relaunch the core script, shuting down and rebooting",
                    "threads"   : "Show active threads",
                    "="        : "========= Pliugins Management =========",
                    "active"    : "show loaded plugins",
                    "stop"      : "Stop an active plugin",
                    "reload"    : "Reload an active plugin",
                    "unload"    : "unload an active plugin",
                    "scan"      : "Scan for new actived/deactived plugins and load/unload them",
                    "=="       : "========= Publish Events =========",
                    "status"    : "Request the status of all plugins",
                    "send"      : "Publish an existing subscribed event",
                    "prompt"    : "start a chat with the LLM, exit with ctrl+c",
                    "==="      : "========= quick keyboard shortcuts =========",
                    "m"         : "Toggle Mute/Unmute TTS",
                    "d"         : "Toggle Deafen/Undeafen STT",
                    "0"         : "Stop current TTS",
                    "===="      : "=========  =========",
                    }
        deafen = True
        muted = True

        while True:
            print("System is running. Available commands:")
            for command, description in cms_list.items():
                print(f"> {command}: {description}")
            cmd = input("Enter a command (exit/reload/...) > ").strip().lower()

            if cmd == "exit":
                break

            elif cmd == "active":
                print(f"Active plugins:")
                for plugin_name in core.plugin_manager.loaded_plugins:
                    print(f"> {plugin_name}")

            elif cmd == "status":
                logger.info(f"'Manually publishing STATUS_CHECK event.'")
                core.event_bus.publish("STATUS_CHECK",{"bool": True})

            elif cmd == "threads":
                logger.info(f"'Manually checking active threads'")
                for threads in core.plugin_manager.module_threads:
                    print(f"> {threads}")
                core.plugin_manager.print_active_threads()

            elif cmd == "reload":
                print(f"Available plugins:")
                plugins = list(core.plugin_manager.loaded_plugins)  # Convert to list for indexing
                for index, plugin_name in enumerate(plugins, start=1):
                    print(f"{index}. {plugin_name}")
                # Get user input
                try:
                    choice = int(input("Enter the number of the plugin to reload: ")) - 1
                    if 0 <= choice < len(plugins):
                        selected_plugin = plugins[choice]
                        logger.info(f"'Manually Reloading plugin {selected_plugin}'...")
                        # Call the function to reload the plugin (assuming a reload function exists)
                        core.plugin_manager.reload_plugin(selected_plugin)
                    else:
                        print("Invalid number. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")


            elif cmd == "unload":
                print(f"Available plugins:")
                plugins = list(core.plugin_manager.loaded_plugins)  # Convert to list for indexing
                for index, plugin_name in enumerate(plugins, start=1):
                    print(f"{index}. {plugin_name}")
                # Get user input
                try:
                    choice = int(input("Enter the number of the plugin to unload: ")) - 1
                    if 0 <= choice < len(plugins):
                        selected_plugin = plugins[choice]
                        logger.info(f"'Manually Unloading plugin {selected_plugin}'...")
                        # Call the function to reload the plugin (assuming a reload function exists)
                        core.plugin_manager.unload_plugin(selected_plugin)
                    else:
                        print("Invalid number. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            elif cmd == "send":
                print(f"Available Subscribers:")
                subscribers = list(core.event_bus._subscribers)  # Convert to a list for indexing
                for index, subscription_name in enumerate(subscribers, start=1):
                    print(f"{index}. {subscription_name}")

                try:
                    choice = int(input("Enter the number of the subscriber to publish (ex. 1 for STATUS_CHECK): ")) - 1
                    if 0 <= choice < len(subscribers):
                        publish_cmd = subscribers[choice]
                        print(f"Selected: {publish_cmd}")

                        # Display message types with numbering
                        types_msg = ["content", "bool", "user", "time", "value"]
                        print("Available Message Types:")
                        for index, msg_type in enumerate(types_msg, start=1):
                            print(f"{index}. {msg_type}")

                        try:
                            type_choice = int(input("Enter the number of the message type: ")) - 1
                            if 0 <= type_choice < len(types_msg):
                                publish_Type = types_msg[type_choice]
                                print(f"Selected Type: {publish_Type}")

                                if publish_Type == "bool":
                                    publish_data = input("bool (True/False): ").strip().capitalize()
                                    if publish_data == "True":
                                        publish_data = True
                                    elif publish_data == "False":
                                        publish_data = False
                                    else:
                                        print(f"'{publish_Type}' is not a valid Boolean")
                                        publish_data = None
                                else:
                                    publish_data = input("Message: ").strip().capitalize()

                                if publish_data is not None:
                                    logger.info(f"Manually publishing {publish_cmd} event with data: {publish_data}")
                                    core.event_bus.publish(publish_cmd, {publish_Type: publish_data})
                            else:
                                print("Invalid message type number. Please try again.")

                        except ValueError:
                            print("Invalid input. Please enter a number for the message type.")

                    else:
                        print("Invalid subscriber number. Please try again.")

                except ValueError:
                    print("Invalid input. Please enter a number for the subscriber.")

            elif cmd == "prompt":
                while True:
                    try:
                        prompt_cmd = input("Prompt (ctrl+c to exit): ").strip()
                        logger.info(f"'Manual prompting the LLM plugin'")
                        prompt = ["Core_terminal", "Lizza Celestia", prompt_cmd, "Text communication from the main terminal"]
                        logger.debug(f"Publishing 'RUN_LLM' event: {prompt}")
                        core.event_bus.publish("RUN_LLM",{"list": prompt})
                    except KeyboardInterrupt:
                        break

            elif cmd == "scan":
                logger.info(f"'Manual rescaning the plugin folder for new plugin'")
                core.plugin_manager.rediscover_plugins()

            elif cmd == "restart":
                logger.info(f"'Manual Full Reboot of plugin list'")
                core.shutdown()
                core.boot()

            elif cmd == "stop":
                print("Available Plugins:")
                plugins = list(core.plugin_manager.loaded_plugins)  # Convert to a list for indexing
                for index, plugin_name in enumerate(plugins, start=1):
                    print(f"{index}. {plugin_name}")

                try:
                    choice = int(input("Enter the number of the plugin to stop: ")) - 1
                    if 0 <= choice < len(plugins):
                        plugin_name = plugins[choice]
                        print(f"Stopping: {plugin_name}")
                        logger.info(f"'Manually stopping plugin {plugin_name}'...")
                        core.event_bus.publish(f"STOP_{plugin_name}", {"bool": True})
                        core.plugin_manager.unload_plugin(plugin_name)
                    else:
                        print("Invalid plugin number. Please try again.")

                except ValueError:
                    print("Invalid input. Please enter a number for the plugin.")
            
        # ============= keyboard shortcut publishes =================
            elif cmd == "m":
                logger.info(f"'Manually publishing MUTE_TTS event: {muted}'")
                core.event_bus.publish("MUTE_TTS",{"bool": muted})
                muted = not muted

            elif cmd == "d":
                logger.info(f"'Manually publishing DEAFEN_STT event: {deafen}'")
                core.event_bus.publish("DEAFEN_STT",{"bool": deafen})
                deafen = not deafen

            elif cmd == "0":
                logger.info(f"'Manually publishing STOP_TTS event: {True}'")
                core.event_bus.publish("STOP_TTS",{"bool": True})






            else:
                logger.warning(f"'{cmd}' is an Unknown command. Available commands:")
                for command, description in cms_list.items():
                    print(f"> {command}: {description}")


            time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("TERMINATING ======================")
    except Exception as e:
        logger.error(f"error: {e}")

    finally:
        logger.info("Shutting down...")
        core.shutdown()
        print("System shutdown complete.")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
