from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "IntelliBI"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-use-env-var"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    POSTGRES_SERVER: str = "localhost"  # Use "db" when running in Docker, "localhost" for local dev
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "intellibi"
    POSTGRES_PASSWORD: str = "intellibi"
    POSTGRES_DB: str = "intellibi"

    # LLM/Chatbot Configuration
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"  # openai, ollama, etc.
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_BASE_URL: str = ""  # For open-source LLMs like Ollama
    CHATBOT_MAX_CONTEXT_MESSAGES: int = 10
    CHATBOT_TEMPERATURE: float = 0.3

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()



