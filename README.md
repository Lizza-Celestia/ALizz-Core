# ALizz-Core
General AI companion plugin manager.


## Installation
Create and activate project environment:
```bash
python -m venv venv_ALizz_Core
.\venv_ALizz_Core\Scripts\activate
python -m pip install --upgrade pip
```
Next install the required dependencies for each plugin (`pip install [Package]`)


## Plugins
Ready made plugins can be found at [ALizz-Plugins](https://github.com/Lizza-Celestia/ALizz-Plugins)

### Custom Plugins
Use the sample_plugin.py script as refence for new custom plugins. 
Naming requirements (Case sensitive) are:
- Folder name: **pluginName**
- script name: **pluginName**_Plugin.py
- class name: class **PluginName**Plugin(BasePlugin)
- __init__: def __init__(self, core, enabled=True):
                self.core = core        # enables the event_bus for pub/sub events
