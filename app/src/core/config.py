from enum import Enum
import os

from pydantic import PostgresDsn
from starlette.config import Config

config = Config(".env")

""" General Configuration """
API_PREFIX = config("API_PREFIX", default="/api")
API_BASE_URL = config("API_BASE_URL", default="")
PROJECT_NAME = config("PROJECT_NAME", default="iFinance")
DEBUG = config("DEBUG", cast=bool, default=True)
VERSION = config("VERSION", default="")
PAGINATION_LIMIT = config("PAGINATION_LIMIT", default=20, cast=int)
GCP_PROJECT_ID = config("PROJECT_ID", default="")

""" Database Configuration """
DB_DRIVER = config("DB_DRIVER", default="postgres")
DB_USERNAME = config("DB_USERNAME", default="postgres")
DB_PASSWORD = config("DB_PASSWORD", default="postgres")
DB_SERVER = config("DB_SERVER", default="127.0.0.1")
DB_PORT = config("DB_PORT", default="5432")
DB_NAME = config("DB_NAME", default="gg_ifinance")
DB_DSN = PostgresDsn.build(
    scheme="postgresql",
    username=DB_USERNAME,
    password=DB_PASSWORD,
    host=f"{DB_SERVER}:{DB_PORT}",
    path=f"{DB_NAME}",
)
DB_POOL_SIZE = config("DB_POOL_SIZE", default=10, cast=int)
DB_MAX_OVERFLOW = config("DB_MAX_OVERFLOW", default=20, cast=int)
DB_POOL_RECYCLE = config("DB_POOL_RECYCLE", default=900, cast=int)

""" REDIS config """
REDIS_DB = config("REDIS_DB", default="0")
REDIS_HOST = config("REDIS_HOST", default="127.0.0.1")
REDIS_PORT = config("REDIS_PORT", default="6379", cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", default="")
REDIS_EXPIRATION_TIME = config("REDIS_EXPIRATION_TIME", default=3600, cast=int)
REDIS_URI = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

""" Google Cloud Storage"""
GOOGLE_APPLICATION_CREDENTIALS = config("GOOGLE_APPLICATION_CREDENTIALS", default="")
GCS_BUCKET_IMAGE_ATTENDANCE = config("GCS_BUCKET_IMAGE_ATTENDANCE", default="")
GCS_BUCKET_IMAGE_VISIT = config("GCS_BUCKET_IMAGE_VISIT", default="")
GCS_BUCKET_IMAGE_CUSTOMER = config("GCS_BUCKET_IMAGE_CUSTOMER", default="")

""" EXTERNAL ENDPOINT """
ORGANIZATION_SERVICE_URL = config(
    "ORGANIZATION_SERVICE_URL", default="")
ORGANIZATION_TOKEN = config("ORGANIZATION_TOKEN", default="")
APP_CODE = config("APP_CODE", default="COLL")
WSO_API_KEY = config("WSO_API_KEY", default="")
MICROESB_URL = config("MICROESB_URL", default="")
MICROESB_API_KEY = config("MICROESB_API_KEY", default="")


CMS_BASE_URL = config("CMS_BASE_URL", default="https://cisdev.dipostar.org")

GEMINI_API_KEY= os.getenv("GEMINI_API_KEY", "")