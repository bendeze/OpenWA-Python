import asyncio
import json
import sys

from redis_client import redis_client, rpc_call, start_redis_listener


async def main():
    class DummySio:
        async def emit(self, *args, **kwargs):
            pass

    task = asyncio.create_task(start_redis_listener(DummySio()))
    await asyncio.sleep(0.5)
    try:
        res = await rpc_call("GET_QR_CODE", {}, timeout=3.0)
        print("RPC RESULT:", res)
    except Exception as e:
        print("RPC ERROR:", repr(e))
    finally:
        task.cancel()
        await redis_client.close()


asyncio.run(main())
