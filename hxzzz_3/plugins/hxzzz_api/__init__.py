import nonebot
from aiohttp import web
import asyncio
import threading



async def handle(request):
    data = await request.json()
    bot = nonebot.get_bot()
    # logger.debug(data['group_id'])
    msg_type = data['type']
    msg = data['message']
    try:
        if msg_type == 1:
            group_id = data['group_id']
            await bot.send_group_msg(group_id=group_id, message=msg)
        elif msg_type == 2:
            user_id = data['user_id']
            await bot.send_private_msg(user_id=user_id, message=msg)
        return web.Response(text="200 ok")
    except Exception as e:
        return web.Response(text=f"{e}")


async def init_app():
    app = web.Application()
    app.router.add_post('/sendmsg', handle)

    return app


async def start_server():
    runner = web.AppRunner(await init_app())
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5050)
    await site.start()
    print("Server started at http://localhost:5050")

    # Run forever
    await asyncio.Event().wait()


async def main():
    await start_server()


def start_asyncio_event_loop():
    asyncio.run(main())


# 启动异步事件循环的线程
thread = threading.Thread(target=start_asyncio_event_loop)
thread.start()
