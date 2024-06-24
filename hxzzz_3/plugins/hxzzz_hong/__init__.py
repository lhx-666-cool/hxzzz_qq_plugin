import random
import string
import time
from typing import Dict
import re

import httpx
from nonebot import get_plugin_config, logger, on_command
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent, MessageEvent, Message, PrivateMessageEvent, \
    Bot
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from .openai import get_chat_response
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="hxzzz_hong",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

# 一些公共变量
default_preset = ""
api_index = -1
# 公共模式
public_mode = False
public_sessionID = 'public_session'
openai_api_key = 'sk-AnAvj3X1dubSa5449891B12731B04aEd94E5F01f8938C621'
inf = 1000000000


class Session:
    chat_count: int = 1
    last_timestamp: int = 0

    def __init__(self, _id):
        self.session_id = _id
        self.preset = default_preset
        self.conversation = []
        self.token_record = []
        self.total_tokens = 0

    # 重置会话
    def reset(self):
        self.conversation = []

    # 会话
    async def get_chat_response(self, msg, is_admin) -> str:
        if openai_api_key == '':
            return f'无API Keys，请在配置文件或者环境变量中配置'

        def check_and_reset() -> bool:
            if is_admin:
                return False
            # 超过一天重置
            from datetime import datetime
            last = datetime.fromtimestamp(self.last_timestamp)
            now = datetime.fromtimestamp(time.time())
            delta = now - last
            if delta.days > 0:
                self.chat_count = 0

            # 一天之内检查次数
            if self.chat_count >= inf:
                return True
            return False

        if check_and_reset():
            return f'每日聊天次数达到上限'

        import tiktoken
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        # 长度超过4096时，删除最早的一次会话
        while self.total_tokens + len(encoding.encode(msg)) > 4096 - 0:
            logger.debug("长度超过4096 - max_token，删除最早的一次会话")
            self.total_tokens -= self.token_record[0]
            del self.conversation[0]
            del self.token_record[0]

        res, ok = await get_chat_response(self.preset,
                                          self.conversation,
                                          msg)
        if ok:
            self.chat_count += 1
            self.last_timestamp = int(time.time())
            # 输入token数
            self.token_record.append(res['usage']['prompt_tokens'] - self.total_tokens)
            # 回答token数
            self.token_record.append(res['usage']['completion_tokens'])
            # 总token数
            self.total_tokens = res['usage']['total_tokens']

            logger.debug(res['usage'])
            logger.debug(self.token_record)
            return self.conversation[-1]['content']
        else:
            # 出现错误自动重置
            self.reset()
            return res


user_session: Dict[str, Session] = {
    public_sessionID: Session(public_sessionID)
}
user_lock = {}


def get_user_session(user_id) -> Session:
    if user_id not in user_session:
        user_session[user_id] = Session(user_id)

    if public_mode:
        return user_session[public_sessionID]
    else:
        return user_session[user_id]


async def handle_msg(resp: str) -> str or MessageSegment:
    return resp


def checker(event: GroupMessageEvent) -> bool:
    return not event.sender.role == "member"


clear = on_command("clear", priority=100, block=True)


@clear.handle()
async def _(matcher: Matcher, event: MessageEvent):
    session_id = event.get_session_id()
    user_lock[session_id] = False


gpt3 = on_command("hong", priority=100, block=True)


@gpt3.handle()
async def _(bot: Bot, matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    session_id = event.get_session_id()
    msg = arg.extract_plain_text().strip()
    logger.debug("session_id")
    logger.debug(session_id)
    if not msg:
        return

    if session_id in user_lock and user_lock[session_id]:
        await matcher.finish("消息太快啦～请稍后", at_sender=True)
    try:
        user_lock[session_id] = True
        resp = await get_user_session(session_id).get_chat_response(msg, checker(event))
        resp = await handle_msg(resp)
        pattern = r'https?:\/\/.*?\.png\b'
        matches = re.findall(pattern, resp)
        has_img = False
        if len(matches) != 0:
            matches = matches[0]
            async with httpx.AsyncClient() as client:
                img_resp = await client.get(matches)
                filename = ''.join(random.sample(string.ascii_letters + string.digits, 8))
                with open('/home/liu/temp/' + filename + '.png', 'wb') as f:
                    f.write(img_resp.content)
                    has_img = True
        # 发送消息
        # 如果是私聊直接发送
        if isinstance(event, PrivateMessageEvent):
            await matcher.send(resp)
        else:
            # 如果不是则以回复的形式发送
            message_id = event.message_id
            await matcher.send(MessageSegment.reply(message_id) + resp)

        user_lock[session_id] = False
        if has_img:
            pic = '[CQ:image,file=file://{}]'.format("/home/liu/temp/" + filename + '.png')
            await matcher.send(MessageSegment.reply(message_id) + Message(pic))
    except Exception as e:
        await matcher.send(f"出错了{e}", at_sender=True)
        user_lock[session_id] = False
