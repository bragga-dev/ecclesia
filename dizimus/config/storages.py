

import os
from storages.backends.s3boto3 import S3Boto3Storage

class MediaFilesStorage(S3Boto3Storage):
    bucket_name = os.environ.get("MINIO_BUCKET_MEDIA", "dizimus-media")
    default_acl = "public-read"
    file_overwrite = False
    custom_domain = os.environ.get("MINIO_PUBLIC_URL")
    url_protocol = os.environ.get("MINIO_URL_PROTOCOL", "http:")

class StaticFilesStorage(S3Boto3Storage):
    bucket_name = os.environ.get("MINIO_BUCKET_STATIC", "dizimus-static")
    default_acl = "public-read"
    file_overwrite = True

class PrivateFilesStorage(S3Boto3Storage):
    bucket_name = os.environ.get("MINIO_BUCKET_PRIVATE", "dizimus-private")
    default_acl = None        
    file_overwrite = False
    querystring_auth = True   
    querystring_expire = 300  


