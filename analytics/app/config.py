from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    duckdb_path: Path = Path("/data/analytics.db")
    sample_data_size: int = 100_000

    class Config:
        env_prefix = "ANALYTICS_"