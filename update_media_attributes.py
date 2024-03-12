from app.src.common.config.database import get_db_session
from app.src.core.repositories.media_repository import MediaRepository
from app.src.common.config.app_settings import get_app_settings
import boto3 as aws
import subprocess
import json
import os
import math


def main() -> None:
    settings = get_app_settings()
    bucket = settings.MEDIA_BUCKET

    client = aws.client("s3", region_name=settings.REGION)
    session = aws.Session()
    print(f"Selected bucket: {bucket}")
    media_repository = MediaRepository()

    media_bucket = session.resource("s3", region_name=settings.REGION).Bucket(bucket)
    for object in media_bucket.objects.all():
        print(f"object={object.key}")
        media_code = object.key.split(".")[0]

        file = "./" + object.key
        client.download_file(bucket, object.key, file)

        command = "ffprobe -v quiet -show_format -print_format json " + file
        process = subprocess.check_output(command, shell=True)
        output = process.decode('utf-8')
        os.remove(file)
        media_attributes = json.loads(output)
        media_length = math.ceil(float(media_attributes.get("format", {}).get("duration")))
        media_size = int(media_attributes.get("format", {}).get("size"))
        print(f"Updating media attributes for media_code: {media_code}", f"{media_size=}", f"{media_length=}")
        media_repository.update_media_attributes(
            media_code,
            media_len=media_length,
            media_size=media_size,
            is_uploaded=True
        )


if __name__ == "__main__":
    main()
