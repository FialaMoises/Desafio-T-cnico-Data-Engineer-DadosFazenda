from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    database: str = "sncr"
    user: str = "sncr_user"
    password: str = "sncr_pass"

    class Config:
        env_prefix = "POSTGRES_"
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    @property
    def connection_string(self) -> str:
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


db_settings = DatabaseSettings()
