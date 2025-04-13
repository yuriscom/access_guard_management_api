import logging
import os
from typing import Optional

from access_guard.utils import parse_policy_loader_type
from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    database_url: str = Field(..., env='DATABASE_URL')
    # adapter_type: Optional[str] = Field(None, env='ADAPTER_TYPE')
    rbac_model_path: Optional[str] = Field(None, env='RBAC_MODEL_PATH')
    development_mode: bool = Field(False, env='DEVELOPMENT_MODE')
    jwt_secret_key: str = Field("your-secret-key", env='JWT_SECRET_KEY')
    POLICY_LOADER_TYPE: str = Field(..., env='POLICY_LOADER_TYPE')

    class Config:
        extra = 'ignore'  # allow unknown env vars
        env_file = '.env'
        env_file_encoding = 'utf-8'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"Loading settings from {os.path.abspath('.env')}")
    #
    # @property
    # def adapter(self):
    #     return parse_adapter_type(self.adapter_type)

    @property
    def policy_loader_type(self):
        return parse_policy_loader_type(self.POLICY_LOADER_TYPE)


# Module-level singleton
_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

settings = get_settings()