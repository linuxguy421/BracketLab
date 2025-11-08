# core/config_manager.py

import json
from pathlib import Path
from typing import Optional
from core.models import TournamentConfig

# Define the DEFAULT path
DEFAULT_CONFIG_PATH = Path('data') / 'config.json'
DEFAULT_CONFIG = TournamentConfig().model_dump_json(indent=4)

class ConfigManager:
    """Manages loading, saving, and accessing the application configuration."""
    
    # Allows path to be injected (for testing purposes)
    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self._config: Optional[TournamentConfig] = None
        self.load_config()

    @property
    def config(self) -> TournamentConfig:
        """Access the loaded configuration model."""
        if not self._config:
            # This should only happen if __init__ failed
            raise RuntimeError("Configuration has not been loaded.")
        return self._config

    def load_config(self):
        """Loads the configuration from a JSON file, creating a default if none exists."""
        if not self.config_path.exists():
            print(f"Configuration file not found at {self.config_path}. Creating default.")
            self.config_path.parent.mkdir(exist_ok=True)
            self.config_path.write_text(DEFAULT_CONFIG)
            self._config = TournamentConfig()
            return

        try:
            config_data = json.loads(self.config_path.read_text())
            # Pydantic validation happens here
            self._config = TournamentConfig.model_validate(config_data)
        except Exception as e:
            print(f"Error loading config: {e}. Falling back to default configuration.")
            self._config = TournamentConfig()

    def save_config(self):
        """Saves the current configuration to the JSON file."""
        if self._config:
            self.config_path.write_text(self._config.model_dump_json(indent=4))

# Initialization for use across the application (uses the default path)
config_manager = ConfigManager()
