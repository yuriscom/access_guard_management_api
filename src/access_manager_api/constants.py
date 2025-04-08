import os
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.parent

# Configuration paths
CONFIG_DIR = ROOT_DIR / "config"
MODEL_PATH = CONFIG_DIR / "rbac_model.conf"

# Ensure the config directory exists
CONFIG_DIR.mkdir(exist_ok=True) 