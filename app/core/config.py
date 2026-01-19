from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_PORT: int = Field(..., env="DB_PORT")
    DB_NAME: str = Field(..., env="DB_NAME")

    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    MAX_UPLOAD_SIZE_MB: int = Field(1024, env="MAX_UPLOAD_SIZE_MB")  # 1 GB
    
    # Password expiration settings (in hours)
    TEMP_PASSWORD_VALIDITY_HOURS: int = Field(24, env="TEMP_PASSWORD_VALIDITY_HOURS")

    @property
    def DATABASE_URL(self) -> str:
        """
        Canonical SQLAlchemy database URL.
        Used by both app runtime and Alembic.
        """
        return (
            f"postgresql+psycopg2://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

