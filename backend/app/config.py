from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    use_openai: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()