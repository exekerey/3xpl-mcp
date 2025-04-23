from pathlib import Path

from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    threexpl_api_key: str = ""
    threexpl_api_base_url: str = "https://api.3xpl.com"
    pagination_limit: int = 25

    @field_validator('threexpl_api_base_url', mode='after')
    def set_api_base_url(cls, v, info: ValidationInfo):
        if not info.data.get("threexpl_api_key"):
            return "https://sandbox-api.3xpl.com"
        return v


env_path = Path(__file__).resolve().parents[2] / ".env"
config = Config(_env_file=env_path)
