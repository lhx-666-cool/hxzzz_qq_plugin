import pymysql
from nonebot import get_plugin_config, on_message, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message, Bot
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
import mysql.connector
from .config import Config
from _datetime import datetime

__plugin_meta__ = PluginMetadata(
    name="hxzzz_chatlog",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


def create_db_connection():
    connection = mysql.connector.connect(
        host='49.235.133.187',  # 通常是localhost
        user='qqlog',
        password='mZYm6WxbMKFnBePb',
        database='qqlog'
    )
    if connection.is_connected():
        return connection


def insert_log(group_id, user_id, msg):
    connection = create_db_connection()
    if connection is not None:
        cursor = connection.cursor()
        time = datetime.now()
        query = "SELECT max(id) FROM qqlog"
        cursor.execute(query)
        insert_id = cursor.fetchone()[0]
        insert_id += 1
        query = "INSERT INTO qqlog (id, user_id, group_id, data, msg) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (insert_id, user_id, group_id, time, msg))
        connection.commit()
        cursor.close()
        connection.close()


log = on_message(priority=100, block=False)


@log.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    try:
        msg = event.message.extract_plain_text()
        logger.debug(event.message_id)
        # logger.debug(dir(event))
        logger.debug(msg)
        user = event.get_session_id().split("_")
        if len(user) == 3:  # 群聊
            group_id = user[1]
            user_id = user[2]
            # insert_log(group_id, user_id, msg)
        elif len(user) == 1:  # 私聊
            group_id = 0
            user_id = user[0]
            # insert_log(group_id, user_id, msg)
        else:
            return
    except Exception as e:
        logger.debug(e)
