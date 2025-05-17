from pydantic_settings import BaseSettings
# base settings class used to load environment variables from .env file

class Settings(BaseSettings):
    database_hostname:str
    database_port:str
    database_password:str
    database_name:str
    database_username:str
    secret_key:str
    algorithm:str
    access_token_expire_minutes:int
    google_client_id:str
    google_client_secret:str
    google_redirect_uri:str

    class Config:
        env_file=".env"

settings=Settings()