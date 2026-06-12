import asyncio

import redis.asyncio as redis


async def main():
    r = redis.from_url("redis://127.0.0.1:6379")
    p = r.pubsub()
    await p.subscribe("test")
    print("subscribed")
    try:
        async for msg in p.listen():
            print(msg)
    except Exception as e:
        print(f"Error: {e}")


asyncio.run(main())
