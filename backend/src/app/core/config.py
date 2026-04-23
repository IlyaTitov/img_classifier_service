from pydantic_settings import BaseSettings


class Setting(BaseSettings):

    datebase_url: str = "sqlite+aiosqlite:///./test.db"
    datebase_echo: bool = True
    upload_dir: str = "D:/img_classifier_service/backend/src/upload"


setting = Setting()
