import json
from functools import lru_cache
from typing import Any

import boto3 as aws

from app.src.common.config.app_settings import get_app_settings


class SecretManager:
    def __init__(self) -> None:
        self.settings = get_app_settings()
        session = aws.session.Session()
        self.client = session.client(
            service_name="secretsmanager",
            region_name=self.settings.REGION
        )

    def _get_db_secret(self, secret: str, name: str) -> Any:
        response = self.client.get_secret_value(
            SecretId=secret
        )
        kvs = json.loads(response.get('SecretString'))

        return kvs.get(name)

    @lru_cache
    def mongo_db_secret(self, name: str) -> Any:
        return self._get_db_secret(self.settings.MONGODB_SECRET, name)

    @lru_cache
    def mysql_db_secret(self, name: str) -> Any:
        return self._get_db_secret(self.settings.MYSQLDB_SECRET, name)


@lru_cache
def get_secret(name: str) -> str:
    settings = get_app_settings()
    if settings.IS_LOCAL:
        kvs = {
            'user': "cns_owner",
            'password': "Cns@123",
            'port': '3306',
            'host': 'localhost'
        }
    else:
        session = aws.session.Session()
        client = session.client(
            service_name="secretsmanager",
            region_name=settings.REGION
        )

        response = client.get_secret_value(
            SecretId=settings.SECRET
        )
        kvs = json.loads(response.get('SecretString'))

    return kvs.get(name)
