import importlib.util
import json
import os
import traceback

PLUGINS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "plugins")
)


class PluginManager:
    def __init__(self):
        self.plugins_metadata = []
        self.loaded_modules = {}

    def scan_and_load(self):
        self.plugins_metadata = []
        self.loaded_modules = {}

        if not os.path.exists(PLUGINS_DIR):
            os.makedirs(PLUGINS_DIR, exist_ok=True)
            return

        for folder_name in os.listdir(PLUGINS_DIR):
            folder_path = os.path.join(PLUGINS_DIR, folder_name)
            if not os.path.isdir(folder_path):
                continue

            plugin_json_path = os.path.join(folder_path, "plugin.json")
            if not os.path.exists(plugin_json_path):
                continue

            try:
                with open(plugin_json_path, "r") as f:
                    metadata = json.load(f)

                # Make sure the ID is correct
                if "id" not in metadata:
                    metadata["id"] = folder_name

                # Load module if enabled
                if metadata.get("status") == "enabled" and "main" in metadata:
                    main_file = os.path.join(folder_path, metadata["main"])
                    if os.path.exists(main_file):
                        spec = importlib.util.spec_from_file_location(
                            metadata["id"], main_file
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        self.loaded_modules[metadata["id"]] = module
                        print(
                            f"[PluginManager] Successfully loaded plugin: {metadata['name']}"
                        )
                    else:
                        metadata["status"] = "error"
                        metadata["error"] = f"Main file {metadata['main']} not found."

                self.plugins_metadata.append(metadata)
            except Exception as e:
                print(f"[PluginManager] Error loading plugin {folder_name}: {e}")
                traceback.print_exc()

    async def dispatch(self, event_name: str, payload: dict):
        for plugin_id, module in self.loaded_modules.items():
            if hasattr(module, "on_event"):
                try:
                    await module.on_event(event_name, payload)
                except Exception as e:
                    print(
                        f"[PluginManager] Error in plugin {plugin_id} during event {event_name}: {e}"
                    )
                    traceback.print_exc()

    def get_all_plugins(self):
        return self.plugins_metadata


# Global singleton
plugin_manager = PluginManager()
plugin_manager.scan_and_load()
