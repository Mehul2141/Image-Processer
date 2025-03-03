from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str
    DB_NAME: str
    IMAGE_UPLOAD_PATH: str

    class Config:
        env_file = ".env"

settings = Settings()
