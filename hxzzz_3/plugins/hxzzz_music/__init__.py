import string
import random

import httpx
import nonebot
from nonebot import get_plugin_config, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment, PrivateMessageEvent
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_command
import re
from .config import Config
import json

__plugin_meta__ = PluginMetadata(
    name="hxzzz_music",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


def handle_resp(resp):
    pattern = r'jQuery\d+_\d+\((.*)\)'
    match = re.match(pattern, resp)

    if match:
        extracted_string = match.group(1)
        try:
            # 将提取的字符串转换为 JSON 格式
            logger.debug(extracted_string)
            json_data = json.loads(extracted_string)
            return json.dumps(json_data, ensure_ascii=False, indent=4)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON data"}, ensure_ascii=False, indent=4)
    else:
        return json.dumps({"error": "No match found"}, ensure_ascii=False, indent=4)


music = on_command("music", priority=100, block=True)


@music.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    msg = msg.split(" ")
    session_id = event.get_session_id()
    bot = nonebot.get_bot()
    if not msg:
        await matcher.finish("插件用法：/music <关键词>\n如：/music 周杰伦\ntips：删掉歌名中的空格")
    if len(msg) > 2:
        await matcher.finish("插件用法：/music <关键词>\n如：/music 周杰伦\ntips：删掉歌名中的空格")

    send_msg = ""
    send_msg_type = 0
    if len(msg) == 1:
        send_msg_type = 1
        try:
            async with httpx.AsyncClient() as client:
                url = "https://music.gdstudio.xyz/api.php?callback=jQuery1113016680113830960963_1715852565390"
                data = {"types": "search", "count": "20", "source": "netease", "page": "1", "name": msg[0]}

                resp = await client.post(url=url, headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
                    "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
                    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin"
                }, data=data)
                resp = json.loads(handle_resp(resp.text))
                music_detail = ""
                cnt = 1
                for i in resp:
                    logger.debug(i)
                    music_detail += str(cnt) + ":" + i['name'] + " | " + ",".join(i['artist']) + '\n'
                    cnt += 1
                send_msg = music_detail
                send_msg += "请输入歌曲候选编号：\n" + "/music " + msg[0] + " x"
        except Exception as e:
            await matcher.finish(f"出错了：{e}\ntips：删掉歌名中的空格")
    elif len(msg) == 2:
        send_msg = 2
        try:
            async with httpx.AsyncClient() as client:
                data = {"types": "search", "count": "20", "source": "netease", "page": "1", "name": msg[0]}
                resp = await client.post(
                    "https://music.gdstudio.xyz/api.php?callback=jQuery1113016680113830960963_1715852565390", data=data)
                resp = json.loads(handle_resp(resp.text))
                logger.debug(resp)
                filename_without_random = resp[int(msg[1]) - 1]['name'] + "_" + ",".join(
                    resp[int(msg[1]) - 1]['artist'])
                filename = filename_without_random + ''.join(random.sample(string.ascii_letters + string.digits, 8))
                music_id = resp[int(msg[1]) - 1]['id']
                logger.debug(music_id)
                data = {"types": "url", "id": music_id, "source": "netease", "br": "999"}
                resp = await client.post(
                    "https://music.gdstudio.xyz/api.php?callback=jQuery111308834949962209979_1715785559472", data=data)
                resp = json.loads(handle_resp(resp.text))
                resp = resp['url']
                logger.debug(resp)
                music_url = resp
                music_resp = await client.get(resp)
                with open('/home/liu/temp/' + filename + '.mp3', 'wb') as f:
                    f.write(music_resp.content)
        except Exception as e:
            await matcher.finish(f"出错了：{e}\ntips：删掉歌名中的空格")
    if isinstance(event, PrivateMessageEvent):
        if send_msg_type == 1:
            await matcher.send(MessageSegment.text(send_msg))
        else:
            await matcher.send(MessageSegment.text(f"即将发送：{filename_without_random}\nurl：{music_url}"))
            await matcher.send(MessageSegment.record("file:///home/liu/temp/" + filename + '.mp3'))
            await bot.upload_private_file(user_id=int(session_id), file='/home/liu/temp/' + filename + '.mp3',
                                          name=filename_without_random + ".mp3")
    else:
        message_id = event.message_id
        if send_msg_type == 1:
            await matcher.send(MessageSegment.reply(message_id) + MessageSegment.text(send_msg))
        else:
            await matcher.send(MessageSegment.reply(message_id) + MessageSegment.text(
                f"即将发送：{filename_without_random}\nurl：{music_url}"))
            await matcher.send(MessageSegment.record("file:///home/liu/temp/" + filename + '.mp3'))
            logger.debug(int(session_id.split('_')[1]))
            await bot.upload_group_file(group_id=int(session_id.split('_')[1]),
                                        file='/home/liu/temp/' + filename + '.mp3',
                                        name=filename_without_random + ".mp3")
