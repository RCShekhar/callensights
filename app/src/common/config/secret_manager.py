import json
from functools import lru_cache

import boto3 as aws

from app.src.common.config.app_settings import get_app_settings


# TODO add decorated exception handling for Client error
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
