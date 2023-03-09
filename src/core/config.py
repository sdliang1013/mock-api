# coding:utf-8

from pydantic import BaseSettings


class Settings(BaseSettings):
    api_base: str = "/api/v1"
    key: str = 'XjgX3zAkA2hDT0ySpzOU1uq3iZ9F6yA9'
    expire_seconds: int = 60 * 60 * 8
    tolerance_seconds: int = 60 * 60
    token_header: str = 'X-Mock-Api'
    white_uris: str = '/api.json'
    debugger: bool = False
    # ryd
    ryd_api: str = ""

    def api_path(self, path: str):
        return self.api_base + path

    class Config:
        env_prefix = 'MOCK_'
        env_file = 'custom.env'
        env_file_encoding = 'utf-8'


settings = Settings()
