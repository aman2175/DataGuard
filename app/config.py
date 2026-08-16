from pydantic_settings import BaseSettings , SettingsConfigDict #pydantic_settings is a library for creating settings classes

class Settings(BaseSettings):# basesettings class inherites from pydantic_settings
    model_config=SettingsConfigDict(env_file=".env", extra="ignore")

    database_url:str# database url for the database
    app_env: str= "development"# environment variable for the application this is optional and has a default value of development

settings=Settings()


