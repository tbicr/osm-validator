import aioredis


class RedisNamespace(object):

    def __init__(self, redis, namespace=None):
        self._redis = redis
        self._namespace = namespace

    def __getattr__(self, item):
        if self._namespace is None:
            namespace = item
        else:
            namespace = '{}:{}'.format(self._namespace, item)
        return RedisNamespace(self._redis, namespace)

    async def set(self, name, *args, **kwargs):
        if self._namespace is None:
            raise TypeError('Out of namespace using')
        return await self._redis.set(
            '{}:{}'.format(self._namespace, name), *args, **kwargs)

    async def get(self, name, *args, **kwargs):
        if self._namespace is None:
            raise TypeError('Out of namespace using')
        return await self._redis.get(
            '{}:{}'.format(self._namespace, name), *args, **kwargs)

    def close(self):
        self._redis.close()

    async def wait_closed(self):
        return await self._redis.wait_closed()


async def setup(app):
    redis = await aioredis.create_redis_pool((
        app.config.REDIS['host'],
        app.config.REDIS['port'],
    ), encoding='utf-8')
    app.redis = RedisNamespace(redis)


async def close(app):
    app.redis.close()
    await app.redis.wait_closed()
    app.redis = None
