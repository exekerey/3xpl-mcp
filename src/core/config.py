from pydantic_settings import BaseSettings


class Config(BaseSettings):
    txpl_api_base_url = "https://sandbox-api.3xpl.com"


config = Config()
