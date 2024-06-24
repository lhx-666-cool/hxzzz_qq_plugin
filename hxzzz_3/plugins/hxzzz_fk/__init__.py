import re

import httpx
from nonebot import get_plugin_config, on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, PrivateMessageEvent, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="hxzzz_fk",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

fk = on_command("fk", priority=100, block=True)


@fk.handle()
async def _(matcher: Matcher, event: MessageEvent):
    async with httpx.AsyncClient() as client:
        success = True
        try:
            resp = await client.get("https://allai.works/api/home_page_content")
            resp = resp.text
            pattern = re.compile(r'https?://demo.[^\s]+\\')
            resp = pattern.findall(resp)
            send_msg = ""
            for i in range(0, len(resp)):
                resp[i] = resp[i].replace('\\', '')
                resp[i] = resp[i].replace('demo.oaifree.com', 'gpt4.hxzzz.site')
                send_msg += resp[i] + "\n"

        except Exception as e:
            success = False

        prompt = "这是一些免费使用gpt4的网站喵，可能可以使用：\n"
        if isinstance(event, PrivateMessageEvent):
            if success:
                await matcher.send(MessageSegment.text(prompt) + MessageSegment.text(send_msg))
            else:
                await matcher.send(MessageSegment.text(f"出错：{e}"))
        else:
            message_id = event.message_id
            if success:
                await matcher.send(MessageSegment.reply(message_id) + MessageSegment.text(prompt) + MessageSegment.text(send_msg))
            else:
                await matcher.send(MessageSegment.reply(message_id) + MessageSegment.text(f"出错：{e}"))
