from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    serpapi_key: str = ""
    serpapi_monthly_ceiling: int = 240
    database_url: str = "sqlite:///./trip_planner.db"
    default_currency: str = "USD"
    fare_ttl_seconds: int = 86400
    validation_tolerance_pct: int = 15
    validation_top_n: int = 5
    envelope_long_gap_days: int = 30
    primary_source: Literal["fli", "fast-flights", "mock"] = "fli"


settings = Settings()
