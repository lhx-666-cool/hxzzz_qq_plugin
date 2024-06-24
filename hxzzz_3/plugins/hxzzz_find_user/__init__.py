from nonebot import get_plugin_config, on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="hxzzz_find_user",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

find_user = on_command("//find", priority=100, block=True)


@find_user.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    msg = args.extract_plain_text().strip()
    if not msg:
        await find_user.finish("请输入user_id")
    else:
        try:
            user_id = int(msg)
        except Exception as e:
            await find_user.send(f"请输入正确的user_id{e}")
            return
        count = 0
        in_group = []
        group_list = await bot.get_group_list()
        for i in group_list:
            group_name = i['group_name']
            group_id = i['group_id']
            group_member_list = await bot.get_group_member_list(group_id=group_id)
            for j in group_member_list:
                group_member_user_id = j['user_id']
                if group_member_user_id == user_id:
                    count += 1
                    in_group.append(f"{group_id}({group_name})")
                    break
        in_group = '\n'.join(in_group)
        user_name = await bot.get_stranger_info(user_id=user_id)
        user_name = user_name['nickname']
        await find_user.send(f"user_id:{user_id}({user_name})所在群有:\n{in_group}\n共{count}个")
        # await find_user.send(Message(MessageSe))
