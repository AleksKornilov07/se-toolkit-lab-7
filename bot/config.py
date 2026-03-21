"""Bot configuration loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration."""

    # Telegram Bot token
    bot_token: str = Field(default="", alias="BOT_TOKEN")

    # LMS API configuration
    lms_api_base_url: str = Field(default="http://localhost:42002", alias="LMS_API_BASE_URL")
    lms_api_key: str = Field(default="", alias="LMS_API_KEY")

    # LLM API configuration (for intent routing)
    llm_api_base_url: str = Field(default="http://localhost:42005/v1", alias="LLM_API_BASE_URL")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_api_model: str = Field(default="coder-model", alias="LLM_API_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = BotSettings.model_validate({})
