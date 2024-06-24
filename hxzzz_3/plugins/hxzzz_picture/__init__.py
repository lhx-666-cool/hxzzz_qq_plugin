import json
import random
import string
import os
import httpx
from nonebot.plugin import PluginMetadata
from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Message, MessageEvent, helpers, MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg
import re
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="hxzzz_picture",
    description="",
    usage="",
    config=Config,
)


def is_url(string):
    return re.match(url_pattern, string) is not None


url_pattern = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # 域名
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...或者ip
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...或者IPv6
    r'(?::\d+)?'  # 可选的端口
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

PzyHelp = on_command("pzyhelp", priority=100, block=True)


@PzyHelp.handle()
async def _(event: MessageEvent):
    msg_id = event.message_id
    await PzyHelp.finish(
        MessageSegment.reply(
            msg_id) + "插件用法：\n/addpzy [图片链接]  # 添加一个pzy\n/pzy  # 获取一个pzy\n图片链接获取方式：图床（https://www.imgtp.com/）")


AddPzy = on_command("addpzy", priority=100, block=True)


@AddPzy.handle()
async def _(event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    msg_id = event.message_id
    msg = args.extract_plain_text().strip().split(" ")
    logger.debug(msg)
    if len(msg) != 1:
        await PzyHelp.send(
            MessageSegment.reply(msg_id) + "插件用法：\n/addpzy [图片链接]  # 添加一个pzy\n/pzy  # 获取一个pzy")
    else:
        if not is_url(msg[0]):
            await AddPzy.send(MessageSegment.reply(msg_id) + "请输入正确的网址")
        else:
            try:
                async with httpx.AsyncClient() as client:
                    logger.debug(msg[0])
                    resp = await client.get(msg[0])
                    logger.debug(resp)
                    filename = ''.join(random.sample(string.ascii_letters + string.digits, 8))
                    with open('/home/liu/temp/pzy/' + filename + '.jpg', 'wb') as f:
                        f.write(resp.content)
                await AddPzy.send(MessageSegment.reply(msg_id) + f"添加pzy成功")

            except Exception as e:
                await AddPzy.send(MessageSegment.reply(msg_id) + f"出现错误{e}")


GetPzy = on_command("///pzy", priority=100, block=True)


@GetPzy.handle()
async def _(event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    msg_id = event.message_id
    msg = args.extract_plain_text().strip()
    cnt = 1
    try:
        cnt = int(msg)
    except Exception as e:
        logger.debug(e)
    if cnt > 5:
        cnt = 5
    try:
        for i in range(0, cnt):
            await send(matcher)
    except Exception as e:
        await AddPzy.send(MessageSegment.reply(msg_id) + f"出现错误{e}")


async def send(matcher):
    dir = "/home/liu/temp/pzy/"
    pzy_list = os.listdir(dir)
    logger.debug(pzy_list)
    random_pzy = random.choice(pzy_list)
    logger.debug(random_pzy)
    pic = '[CQ:image,file=file://{}]'.format(dir + random_pzy)
    await matcher.send(Message(pic))

# pictrans= on_command("分析图片", priority=5, block=False,aliases={"翻译图片"})
#
#
# @pictrans.handle()
# async def _(event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
#     if event.reply and event.reply.message.count('image'):
#         img = event.reply.message.get('image', 1)
#         logger.debug("get img")
#         logger.debug(img)
#     else:
#         logger.debug(event.reply)
#         # logger.debug(event.reply.message.count('image'))
#         logger.debug(event.message)


# @pictrans.got("img_list", prompt="请发送要分析的图片")
# async def handle_event(self, event: MessageEvent, img_list: list = Arg()):
#     pass
# try:
#     img_url_list = helpers.extract_image_urls(event.message)
#     if not img_url_list:
#         img_url_list = img_list
#     logger.debug(img_url_list)
#     resp = await get_chat_response(img_url_list[0])
#     await pictrans.finish(message=MessageSegment.image(img_url_list[0]) + MessageSegment.text(resp[0]), reply=True)
# except MatcherException:
#     raise
# except Exception as e:
#     logger.warning(f"分析失败:{e}")
#     await pictrans.send(f"分析失败: {e}")


# async def get_chat_response(msg: str):
#     openai_client = AsyncOpenAI(
#         api_key="sk-D44S9HD3jbnyO2cL87Ce77D5F437433f8f8073475999D06a",
#         base_url="https://newapi.hxzzz.asia/v1",
#         max_retries=5,
#     )
#     try:
#         logger.debug(msg)
#         conversation = [
#             {"role": "user",
#              "content": f"{msg} 这张图片是什么意思"}
#         ]
#
#         response = await openai_client.chat.completions.create(
#             model="st",
#             messages=conversation,
#         )
#         resp = response.json()
#         resp = json.loads(resp)
#         logger.debug(resp['choices'][0]['message']['content'])
#         sendmsg = resp['choices'][0]['message']['content']
#         return sendmsg, True
#     except httpx.ConnectTimeout as e:
#         return f"发生HTTP超时错误: {e.request.url}", False
#     except Exception as e:
#         return f"发生未知错误: {type(e)} {e}", False
