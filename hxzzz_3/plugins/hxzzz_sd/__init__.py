import random
import string

import httpx
from nonebot import get_plugin_config, on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="hxzzz_sd",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

sd = on_command("sd", priority=100, block=False)

@sd.handle()
async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    msg_id = event.message_id
    url = r"https://api.cloudflare.com/client/v4/accounts/984cf68fedad72060d333e51ae837f99/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"
    try:
        async with httpx.AsyncClient() as client:
            img_resp = await client.post(url=url, json={"prompt": msg}, timeout=60, headers={"Authorization": "Bearer 5uQR86g8IwZlZejkRCLPT8-fsos6S15NVTPLxPtE"})
            filename = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            with open('/home/liu/temp/' + filename + '.png', 'wb') as f:
                f.write(img_resp.content)
            pic = '[CQ:image,file=file://{}]'.format("/home/liu/temp/" + filename + '.png')
            await sd.send(MessageSegment.reply(msg_id) + Message(pic))
    except Exception as e:
        await sd.send(MessageSegment.reply(msg_id) + f"出现错误{e}")
