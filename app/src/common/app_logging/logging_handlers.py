import watchtower
import boto3 as aws

from app.src.common.config import SERVICE_NAME, APP_NAME

cw_handler = watchtower.CloudWatchLogHandler(
    log_group=APP_NAME + '/' + SERVICE_NAME,
    boto3_client=aws.client("logs", region_name="us-east-1")
)
