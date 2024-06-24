import base64
import json
import hashlib
import random
import string

from nonebot import get_plugin_config, on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message, PrivateMessageEvent, MessageSegment
from nonebot.exception import FinishedException
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from openai import AsyncOpenAI
import mysql.connector
from mysql.connector import Error
from .config import Config


def create_db_connection():
    connection = mysql.connector.connect(
        host='49.235.133.187',  # 通常是localhost
        user='mars',
        password='YSYFdbFf4r2TfCaD',
        database='mars'
    )
    if connection.is_connected():
        return connection


def insert_translation(yw, hxw, hxwhash, ywhash):
    connection = create_db_connection()
    if connection is not None:
        cursor = connection.cursor()
        query = "INSERT INTO mars (yw, hxw, hxwhash, ywhash) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (yw, hxw, hxwhash, ywhash))
        connection.commit()
        cursor.close()
        connection.close()


def get_original_text(hxwhash):
    connection = create_db_connection()
    if connection is not None:
        cursor = connection.cursor()
        query = "SELECT yw FROM mars WHERE hxwhash = %s"
        cursor.execute(query, (hxwhash,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] if result else None
    return None


def get_martian_text(ywhash):
    connection = create_db_connection()
    if connection is not None:
        cursor = connection.cursor()
        query = "SELECT hxw FROM mars WHERE ywhash = %s"
        cursor.execute(query, (ywhash,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] if result else None
    return None

def translate_to_martian(text):
    random.seed()  # 使用输入长度作为随机种子
    martian_text = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=len(text) * 5))
    return martian_text


__plugin_meta__ = PluginMetadata(
    name="hxzzz_translate",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

tran = on_command("tran", priority=100, block=True)


@tran.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    msg = msg.split(" ")
    if len(msg) < 2:
        err = "插件使用方法：/tran 要翻译的语言 文本\n例如：/tran 英文 你好"
        if isinstance(event, PrivateMessageEvent):
            await matcher.send(err)
        else:
            message_id = event.message_id
            await matcher.send(MessageSegment.reply(message_id) + err)
    else:
        target_lan = msg[0]
        text = ' '.join(msg[1:])
        openai_client = AsyncOpenAI(
            api_key="sk-suVkkUhBvjhsONtr579c8923700248A89620CaA411Ce5bF9",
            base_url="https://newapi.hxzzz.asia/v1",
            max_retries=3,
        )
        system = [
            {"role": "system",
             "content": "You are a professional, authentic translation engine. You only return the translated text, without any explanations."}
        ]
        conversation = [
            {"role": "user",
             "content": f"Please translate into {target_lan} (avoid explaining the original text):\n{text}"}
        ]
        try:
            if target_lan == 'md5':
                md5_hash = hashlib.md5()
                md5_hash.update(text.encode('utf-8'))
                sendmsg = md5_hash.hexdigest()
            elif target_lan == 'base64':
                sendmsg = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            elif target_lan == 'sha256':
                sendmsg = hashlib.sha256(text.encode('utf-8')).hexdigest()
            elif target_lan == '火星文':
                logger.debug(text)
                md5_hash = hashlib.md5()
                md5_hash.update(text.encode('utf-8'))
                ywhash = md5_hash.hexdigest()
                hxw_ = get_martian_text(ywhash)
                if hxw_ is None:
                    hxw = translate_to_martian(text)
                    md5_hash = hashlib.md5()
                    md5_hash.update(hxw.encode('utf-8'))
                    hxwhash = md5_hash.hexdigest()
                    insert_translation(text, hxw, hxwhash, ywhash)
                    sendmsg = hxw
                else:
                    sendmsg = hxw_
            elif target_lan == '地球文':
                hxw = text
                md5_hash = hashlib.md5()
                md5_hash.update(hxw.encode('utf-8'))
                hxwhash = md5_hash.hexdigest()
                yw = get_original_text(hxwhash)
                if yw is None:
                    yw = "火星人没听懂哦"
                sendmsg = yw
            else:
                is_language_prompt = "\"" + target_lan + "\"是真实世界中的一种自然语言的名字吗"
                is_language = await openai_client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=[{"role": "user", "content": is_language_prompt}]
                )
                is_language_resp = is_language.json()
                is_language_resp = json.loads(is_language_resp)
                is_language_resp = is_language_resp['choices'][0]['message']['content']
                if is_language_resp.find("不") != -1 and target_lan != '古汉语' and target_lan != '文言文':
                    if isinstance(event, PrivateMessageEvent):
                        await tran.finish("请输入一种语言")
                    else:
                        message_id = event.message_id
                        await tran.finish(MessageSegment.reply(message_id) + "请输入一种语言")
                response = await openai_client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=system + conversation,
                )
                resp = response.json()
                resp = json.loads(resp)
                logger.debug("111")
                logger.debug(resp['choices'][0]['message']['content'])
                sendmsg = resp['choices'][0]['message']['content']
            if isinstance(event, PrivateMessageEvent):
                await matcher.send(sendmsg)
            else:
                message_id = event.message_id
                await matcher.send(MessageSegment.reply(message_id) + sendmsg)
        except FinishedException:
            pass
        except Exception as e:
            if isinstance(event, PrivateMessageEvent):
                await matcher.send(f"出现错误：{e}")
            else:
                message_id = event.message_id
                await matcher.send(MessageSegment.reply(message_id) + f"出现错误：{e}")
