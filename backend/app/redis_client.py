"""Redis connection for RQ"""
import os
from redis import Redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Redis connection for RQ
redis_conn = Redis.from_url(REDIS_URL)
