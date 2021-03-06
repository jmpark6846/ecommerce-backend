from .base import *

DEBUG = False
ALLOWED_HOSTS = [
    'lk3n4duaxk.execute-api.ap-northeast-2.amazonaws.com'
]
JWT_AUTH_SECURE = True
JWT_AUTH_SAMESITE = 'None'
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'

# django staticfiles
YOUR_S3_BUCKET = "ecommerce--5on7d983s"
STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"
AWS_S3_BUCKET_NAME_STATIC = YOUR_S3_BUCKET
AWS_S3_CUSTOM_DOMAIN = False
STATIC_URL = "https://%s.s3.amazonaws.com/" % YOUR_S3_BUCKET
AWS_S3_MAX_AGE_SECONDS_STATIC = "94608000"

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_QUERYSTRING_AUTH = True