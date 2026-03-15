from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    duckdb_path: Path = Path("/data/analytics.db")
    sample_data_size: int = 100_000

    class Config:
        env_prefix = "ANALYTICS_"
<<<<<<< HEAD
<<<<<<< HEAD
# history: feat: add ExperimentConfig dataclass and validation
=======
# history: feat: integrate cohort analyzer into main pipeline
>>>>>>> feature/cohorts
=======
# history: feat: add config thresholds for recommendation scoring
>>>>>>> feature/recommendation-engine
