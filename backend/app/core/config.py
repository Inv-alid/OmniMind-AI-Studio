from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None

    ollama_base_url: str = "http://localhost:11434"
    lmstudio_base_url: str = "http://localhost:1234/v1"
    llamacpp_base_url: str = "http://localhost:8080"

    chroma_persist_dir: str = "./data/chroma"
    max_concurrent_agents: int = 6
    enable_terminal_tools: bool = False
    enable_file_access: bool = False
    battle_mode_models: List[str] = ["gpt-4o", "claude-3-5-sonnet-20241022", "grok-2"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
