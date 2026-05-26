from pydantic_settings import BaseSettings, SettingsConfigDict

# uma forma mais morderna e segura de utilizar variaveis de ambiente
# consegue acesssar fazendo settings.db


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )
    # consegue rodar o banco sqlite com
    # python -m sqlite3 <nome_banco>
    DATABASE_URL: str
    SECRET_KEY: str
    ACESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
