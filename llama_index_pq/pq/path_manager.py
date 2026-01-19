import os
import platform
import shutil
from pathlib import Path

class PathManager:
    def __init__(self):
        self.os_name = platform.system()
        # Base dir is where this file is located (llama_index_pq/pq/)
        self.base_dir = Path(__file__).resolve().parent

        # Default paths (Windows / Development / Fallback)
        self.config_dir = self.base_dir / 'settings'
        self.data_dir = self.base_dir / 'settings' # Currently data.json is here
        self.log_dir = self.base_dir.parent # llama_index_pq/
        self.cache_dir = Path(os.getcwd()) / 'installer_cache'

        if self.os_name == 'Linux':
            self.setup_linux_paths()

    def setup_linux_paths(self):
        # XDG Config
        xdg_config = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        new_config_dir = Path(xdg_config) / 'prompt_quill'

        # XDG Data
        xdg_data = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        new_data_dir = Path(xdg_data) / 'prompt_quill' / 'data'
        new_log_dir = Path(xdg_data) / 'prompt_quill' / 'logs'

        # XDG Cache
        xdg_cache = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
        new_cache_dir = Path(xdg_cache) / 'prompt_quill'

        # Ensure directories exist
        try:
            new_config_dir.mkdir(parents=True, exist_ok=True)
            new_data_dir.mkdir(parents=True, exist_ok=True)
            new_log_dir.mkdir(parents=True, exist_ok=True)
            new_cache_dir.mkdir(parents=True, exist_ok=True)

            # Migration: If local settings exist and XDG doesn't, copy them
            local_settings = self.config_dir / 'settings.dat'
            xdg_settings = new_config_dir / 'settings.dat'
            if local_settings.exists() and not xdg_settings.exists():
                shutil.copy2(local_settings, xdg_settings)

            # Migration: Presets
            local_presets = self.config_dir / 'presets'
            xdg_presets = new_config_dir / 'presets'
            if local_presets.exists() and not xdg_presets.exists():
                shutil.copytree(local_presets, xdg_presets)

            # Migration: data.json
            local_data = self.data_dir / 'data.json'
            xdg_data_file = new_data_dir / 'data.json'
            if local_data.exists() and not xdg_data_file.exists():
                shutil.copy2(local_data, xdg_data_file)

            # Assign new paths
            self.config_dir = new_config_dir
            self.data_dir = new_data_dir
            self.log_dir = new_log_dir
            self.cache_dir = new_cache_dir

        except Exception as e:
            print(f"Error setting up Linux paths: {e}. Falling back to local paths.")

# Singleton instance
paths = PathManager()
