from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_url: str = "https://data-engineer-challenge-production.up.railway.app"
    delay_seconds: float = 0.5
    delay_random_range: float = 0.3
    max_retries: int = 3
    max_rounds: int = 10

    proxy_list: str = ""
    use_proxy_rotation: bool = False
    use_random_user_agent: bool = True

    output_dir: Path = Path("extractor/output")
    checkpoint_dir: Path = Path("extractor/checkpoints")
    log_dir: Path = Path("extractor/logs")

    class Config:
        env_prefix = "SNCR_"
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()

for directory in [settings.output_dir, settings.checkpoint_dir, settings.log_dir]:
    directory.mkdir(parents=True, exist_ok=True)
