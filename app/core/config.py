from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Billing System"

    # PostgreSQL settings
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "mallow_tect"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "root"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Email settings (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "billing@example.com"

    # Default denominations available in the shop
    DENOMINATIONS: list[int] = [500, 200, 100, 50, 20, 10, 5, 2, 1]

    class Config:
        env_file = ".env"


settings = Settings()
