from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import BaseModel


class Settings(BaseSettings):
    ''' Enviroment settings '''
    BOT_TOKEN: str = ""
    DB_HOST: str = "127.0.0.1"
    DB_USERNAME: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "finance"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False
    )


settings = Settings()