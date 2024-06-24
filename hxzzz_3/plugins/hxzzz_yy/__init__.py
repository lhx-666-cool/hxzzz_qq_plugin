import nonebot
from nonebot import get_plugin_config, on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message, PrivateMessageEvent, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .config import Config

import yinglish

__plugin_meta__ = PluginMetadata(
    name="hxzzz_yy",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

yy = on_command("yy", priority=100, block=True)


@yy.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    if not msg:
        return
    try:
        resp_s = yinglish.chs2yin(msg)
        if isinstance(event, PrivateMessageEvent):
            await matcher.send(resp_s)
        else:
            message_id = event.message_id
            await matcher.send(MessageSegment.reply(message_id) + resp_s)
    except Exception as e:
        await matcher.send(f"error: {e}", )
