from pydantic_settings import BaseSettings


class Setting(BaseSettings):

    datebase_url: str = "sqlite+aiosqlite:///./test.db"
    datebase_echo: bool = True


setting = Setting()
