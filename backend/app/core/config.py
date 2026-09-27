from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "digital-twin-backend"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = ""
    supabase_url: str = "https://example.supabase.co"
    supabase_key: str = "replace-me"
    groq_api_key: str = "replace-me"
    model_path: str = "app/ml/artifacts/risk_model.joblib"
    cors_origins: str = "http://localhost:3000"
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", protected_namespaces=())

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings()
