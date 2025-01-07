from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    DATABASE_NAME: str = "chatgpt_history"
    API_KEY: str
    CORS_ORIGINS: list[str] = ["chrome-extension://"]

    class Config:
        env_file = ".env"

settings = Settings() 