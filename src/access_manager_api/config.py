from typing import Optional

from access_guard.utils import parse_adapter_type
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(..., env='DATABASE_URL')
    adapter_type: Optional[str] = Field(None, env='ADAPTER_TYPE')
    rbac_model_path: Optional[str] = Field(None, env='RBAC_MODEL_PATH')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    @property
    def adapter(self):
        return parse_adapter_type(self.adapter_type)


settings = Settings() 