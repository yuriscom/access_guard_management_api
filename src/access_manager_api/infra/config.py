import json
import logging
from pathlib import Path
from typing import Any, List, Optional

from access_guard.utils import parse_policy_loader_type
from pydantic import BaseModel

from access_manager_api.infra.app_context import get_root_path
from access_manager_api.infra.constants import ENV_DEV, ENV_DEMO, ENV_STAGING, ENV_PROD, ENV_LOCAL

DEFAULT_CONFIG_PATH_STR = "/config/config.json"
logger = logging.getLogger(__name__)




class AccessManagerSettings(BaseModel):
    PolicyLoaderType: str

    @property
    def policy_loader_type(self):
        return parse_policy_loader_type(self.PolicyLoaderType)


class RedisSettings(BaseModel):
    Port: int
    IPs: List[str]


class MailmanSettings(BaseModel):
    SendGridKey: str


class OktaSettings(BaseModel):
    ClientId: str


class CoreDBSettings(BaseModel):
    Host: str
    Port: int
    User: str
    Password: str
    Database: str

    @property
    def URI(self):
        return (
            f"postgresql://{self.User}:{self.Password}@"
            f"{self.Host}:{self.Port}/{self.Database}"
        )

class Infra(BaseModel):
    Environment: Optional[str] = None
    DevelopmentMode: Optional[bool] = False



class AppConfig(BaseModel):
    Infra : Infra
    AccessManager: AccessManagerSettings
    Redis: RedisSettings
    Mailman: MailmanSettings
    Okta: Optional[OktaSettings] = None
    CoreDB: CoreDBSettings
    Apps: Optional[Any] = None

    def get_env(self):
        if self.Infra.Environment in ["development", "dev"]:
            return ENV_DEV
        elif self.Infra.Environment in ["demo"]:
            return ENV_DEMO
        elif self.Infra.Environment in ["staging", "stag"]:
            return ENV_STAGING
        elif self.Infra.Environment in ["production", "prod"]:
            return ENV_PROD
        else:
            return ENV_LOCAL

    def is_env_prod(self) -> bool:
        return self.get_env() == ENV_PROD

    def is_development_mode(self) -> bool:
        return self.Infra.DevelopmentMode


def _get_config_file(path: Path) -> Optional[Path]:
    """Get the config file from the given path."""
    resolved_path = path.resolve()
    logger.info(f"Looking for config file at {resolved_path}")
    if not resolved_path.exists():
        logger.error(f"Config file {resolved_path} does not exist")
        return None

    logger.info(f"Found config file at {resolved_path}")
    return resolved_path


def _get_settings_data() -> dict:
    """Get the settings data from the JSON file."""

    # Try loading from default path (e.g., in K8s)
    config_file_path = _get_config_file(path=Path(DEFAULT_CONFIG_PATH_STR))

    # Fallback to local dev path (repo root + /config/config.json)
    if config_file_path is None:
        fallback_path = Path(f"{get_root_path()}{DEFAULT_CONFIG_PATH_STR}").resolve()
        config_file_path = _get_config_file(path=fallback_path)

    if config_file_path is None:
        raise FileNotFoundError("Config file not found in either default or fallback path.")

    with open(config_file_path, "r") as json_file:
        data = json.load(json_file)

    logger.info("Config file loaded successfully")
    return data


# Load the settings from the JSON file
settings = AppConfig(**_get_settings_data())
logger.info(f"Running in environment: {settings.get_env()}")
