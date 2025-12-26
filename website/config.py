from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	DB_NAME: str
	SECRET_KEY: str
	PORT: int
	DEFAULT_K: int

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)

settings = Settings()