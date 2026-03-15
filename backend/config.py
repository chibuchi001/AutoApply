from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Nova Act
    nova_act_api_key: str = ""

    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "us.amazon.nova-2-lite-v1:0"

    # Database
    database_url: str = "postgresql+asyncpg://autoapply:password@localhost:5432/autoapply"

    # App
    secret_key: str = "changeme"
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"

    # S3
    s3_bucket_name: str = "autoapply-resumes"
    s3_region: str = "us-east-1"

    # Job search
    max_parallel_sessions: int = 3
    application_delay_seconds: int = 2

    @property
    def cors_origins_list(self) -> List[str]:
        origins = [o.strip() for o in self.cors_origins.split(",")]
        # In development, also allow common local dev URLs
        if self.app_env == "development":
            dev_origins = [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:4000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
                "http://127.0.0.1:4000",
            ]
            for o in dev_origins:
                if o not in origins:
                    origins.append(o)
        return origins


settings = Settings()