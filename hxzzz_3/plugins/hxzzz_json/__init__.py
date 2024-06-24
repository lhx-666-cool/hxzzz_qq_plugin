from nonebot import get_plugin_config, on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="hxzzz_json",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

json_ = on_command("json", priority=100, block=True)


@json_.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    if not msg:
        return
    try:
        msg = msg.replace(",", "&#44;").replace("&", "&amp;")
        msg = msg.replace("[", "&#91;").replace("]", "&#93;")
        res = f'[CQ:json,data={msg}]'
        await json_.send(Message(res))
    except Exception as e:
        await matcher.send(f"error: {e}", )
