#!/bin/zsh

MYSQLDB_SECRET="callensights/mysql"
MONGODB_SECRET="callensights/mongodb"
CLERK_SECRET="callensights/clerk/dev"
CLERK_AUDIENCE="callensights-api-dev"
REGION="us-east-1"
DEFAULT_SCHEMA="callensights_dev"
MEDIA_BUCKET="callensights-media"
TRANSCRIPT_BUCKET="callensights-transcript"
ANALYSIS_BUCKET="callensights-analysis"
MEDIA_MIN_SIZE=1024
MEDIA_MAX_SIZE=1073741824

export MEDIA_BUCKET MYSQLDB_SECRET MONGODB_SECRET CLERK_AUDIENCE CLERK_SECRET REGION
export ANALYSIS_BUCKET MEDIA_MAX_SIZE MEDIA_MIN_SIZE DEFAULT_SCHEMA TRANSCRIPT_BUCKET

uvicorn application:application --port 8001 --reload