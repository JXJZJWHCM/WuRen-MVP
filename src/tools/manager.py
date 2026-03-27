import os
import yaml
import glob
from typing import Dict, Any, List

class ToolManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.tools = {}
        self.load_tools()

    def load_tools(self):
        """Loads all YAML tool definitions from the config directory."""
        self.tools = {}
        pattern = os.path.join(self.config_path, "*.yaml")
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tool_def = yaml.safe_load(f)
                    if 'name' in tool_def:
                        self.tools[tool_def['name']] = tool_def
            except Exception as e:
                print(f"Error loading tool from {file_path}: {e}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns a list of available tool definitions."""
        return list(self.tools.values())

    def get_tool(self, name: str) -> Dict[str, Any]:
        """Returns a specific tool definition by name."""
        return self.tools.get(name)

    def get_tool_names(self) -> List[str]:
        return list(self.tools.keys())
