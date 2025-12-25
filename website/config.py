from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	DB_NAME = str
	SECRET_KEY = str
	PORT = int
	DEFAULT_K = int

class Config:
	env_file = ".env"
	env_file_encoding = "utf_8"

settings = Settings()