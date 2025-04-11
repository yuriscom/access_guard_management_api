from typing import Optional

from access_guard.utils import parse_adapter_type, parse_casbin_adapter_type
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(..., env='DATABASE_URL')
    adapter_type: Optional[str] = Field(None, env='ADAPTER_TYPE')
    rbac_model_path: Optional[str] = Field(None, env='RBAC_MODEL_PATH')
    development_mode: bool = Field(False, env='DEVELOPMENT_MODE')
    jwt_secret_key: str = Field("your-secret-key", env='JWT_SECRET_KEY')
    casbin_adapter_type: Optional[str] = Field(None, env='CASBIN_ADAPTER_TYPE')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    @property
    def adapter(self):
        return parse_adapter_type(self.adapter_type)

    @property
    def casbin_adapter(self):
        return parse_casbin_adapter_type(self.casbin_adapter_type)


settings = Settings() 