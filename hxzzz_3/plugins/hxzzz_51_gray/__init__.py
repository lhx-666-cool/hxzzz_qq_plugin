from matplotlib import pyplot as plt, patches
from nonebot import get_plugin_config, on_message, on_command, logger
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="hxzzz_51_gray",
    description="",
    usage="",
    config=Config,
)

import random
import string

config = get_plugin_config(Config)

rank = {}
game_state = {}
correct = {}
combo = {}

async def start_game_func(group, user):
    user_id = group + "_" + user
    game_state[user_id] = [0, 256]
    combo[user_id] = 0
    color1 = random.randint(0, 100)
    color2 = random.randint(156, 256)
    game_state[user_id] = [color1, color2]
    color1 = hex(color1)
    color2 = hex(color2)
    color1 = color1[2:].rjust(2, '0')
    color2 = color2[2:].rjust(2, '0')
    res = await draw_pic(color1, color2, user_id)
    return res

async def gaming(group, user, msg):
    user_id = group + "_" + user
    if user_id not in game_state:
        return "请先开始游戏 /51"
    else:
        if msg == correct[user_id]:
            color1 = game_state[user_id][0]
            color2 = game_state[user_id][1]

            n_color1 = random.randint(color1, (color1 + color2) // 2)
            n_color2 = random.randint((color1 + color2) // 2, color2)
            if n_color2 == n_color2:
                n_color1 -= 1
            game_state[user_id] = [n_color1, n_color2]
            logger.debug("color1" + str(n_color1))
            logger.debug("color2" + str(n_color2))

            n_color1 = hex(n_color1)
            n_color2 = hex(n_color2)
            n_color1 = n_color1[2:].rjust(2, '0')
            n_color2 = n_color2[2:].rjust(2, '0')
            res = await draw_pic(n_color1, n_color2, user_id)
            combo[user_id] += 1
            return f"连胜:{combo[user_id]},回答正确，请继续\n" + res
        else:
            return f"连胜:{combo[user_id]},猜测错误，答案为{correct[user_id]}"
start_game = on_command("51", priority=30, block=False)


@start_game.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    # try:
        msg = args.extract_plain_text().strip()
        msg_id = event.message_id
        user = event.get_session_id().split("_")
        if len(user) == 3:  # 群聊
            group_id = user[1]
            user_id = user[2]
            logger.debug(msg)
            if msg == "":
                res = await start_game_func(group_id, user_id)
                tip_str = "欢迎来到51度灰游戏，你只需要发送/51 [number]，选择你认为和其他颜色不一样的编号即可\n"
                await start_game.send(MessageSegment.reply(msg_id) + tip_str + Message(res))
            else:
                try:
                    msg = int(msg)
                except Exception as e:
                    await start_game.send(MessageSegment.reply(msg_id) + Message("请输入整数"))
                    return
                if msg > 4 or msg < 1:
                    await start_game.send(MessageSegment.reply(msg_id) + Message("请输入1-4整数"))
                else:
                    res = await gaming(group_id, user_id, msg)
                    await start_game.send(MessageSegment.reply(msg_id) + Message(res))
        elif len(user) == 1:  # 私聊
            group_id = 0
            user_id = user[0]
        else:
            pass
    # except Exception as e:
    #     logger.debug(e)


async def draw_pic(color1, color2, user_id):
    # 创建一个新的图和子图
    fig, ax = plt.subplots(figsize=(10, 10))

    # 关闭坐标轴
    ax.axis('off')

    dif = random.randint(0, 3)
    correct[user_id] = dif + 1
    if random.randint(1, 2) == 1:
        temp = color1
        color1 = color2
        color2 = temp

    rect = [patches.Rectangle((0.1, 0.6), 0.3, 0.3, linewidth=0, edgecolor='none', facecolor='#000000' + color1),
            patches.Rectangle((0.6, 0.6), 0.3, 0.3, linewidth=0, edgecolor='none', facecolor='#000000' + color1),
            patches.Rectangle((0.1, 0.1), 0.3, 0.3, linewidth=0, edgecolor='none', facecolor='#000000' + color1),
            patches.Rectangle((0.6, 0.1), 0.3, 0.3, linewidth=0, edgecolor='none', facecolor='#000000' + color1)]
    # 创建四个矩形色块，颜色用十六进制表示，含有透明度
    x = 0.1
    if dif % 2 == 1:
        x = 0.6
    y = 0.1
    if dif <= 1:
        y = 0.6
    rect[dif] = patches.Rectangle((x, y), 0.3, 0.3, linewidth=0, edgecolor='none', facecolor='#000000' + color2)
    # 添加矩形到子图
    ax.add_patch(rect[0])
    ax.add_patch(rect[1])
    ax.add_patch(rect[2])
    ax.add_patch(rect[3])

    # 设置显示区域的范围
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 设置图形为正方形
    ax.set_aspect('equal')

    # 去除图像周围的边框
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=-10, wspace=0)

    filename = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    plt.savefig('/home/liu/temp/' + filename + '.png')
    pic = '[CQ:image,file=file://{}]'.format("/home/liu/temp/" + filename + '.png')
    return pic

# await sd.send(MessageSegment.reply(msg_id) + Message(pic))
