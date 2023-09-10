import os

from redis.asyncio import from_url


redis_connection = from_url(f'redis://{os.environ["REDIS_HOST"]}')
