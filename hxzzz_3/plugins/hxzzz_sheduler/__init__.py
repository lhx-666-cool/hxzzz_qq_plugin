import datetime
import json
import random

import nonebot
from lxml import etree
from nonebot import get_plugin_config, logger
from nonebot.plugin import PluginMetadata
from nonebot import require
import httpx
from openai import AsyncOpenAI

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="hxzzz_sheduler",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


# 基于装饰器的方式
# @scheduler.scheduled_job("cron", hour="*/1", minute="0", second="0", id="job_0")
async def run_every_hour():
    hour = datetime.datetime.now().hour
    if hour in [1, 2, 3, 4, 5, 6, 7]:
        return
    async with httpx.AsyncClient() as client:
        try:
            first_page = await client.get("https://codeforces.com/problemset?tags=combine-tags-by-or,graph matchings,graphs,1200-1600")
            first_page = first_page.text
            first_page_html = etree.HTML(first_page)
            max_page = first_page_html.xpath(r'//*[@id="pageContent"]/div[3]/ul/li/span/a/text()')
            logger.debug(max_page[-1])
            page = random.choices(range(1, int(max_page[-1]) + 1))
            url = f"https://codeforces.com/problemset/page/{page[0]}?tags=combine-tags-by-or,graph matchings,graphs,1200-1600"
            logger.debug(url)
            choice_page = await client.get(url)
            choice_page = choice_page.text
            choice_page_html = etree.HTML(choice_page)
            problem_list_name = choice_page_html.xpath(
                '//*[@id="pageContent"]/div[2]/div[6]/table/tr/td[2]/div[1]/a/text()')
            problem_list_url = choice_page_html.xpath('//*[@id="pageContent"]/div[2]/div[6]/table/tr/td[2]/div[1]/a/@href')
            for i in range(0, len(problem_list_name)):
                problem_list_name[i] = problem_list_name[i].strip()
            for i in range(0, len(problem_list_url)):
                problem_list_url[i] = "https://codeforces.com" + problem_list_url[i]
            choice_problem = random.choices(range(0, len(problem_list_url)))[0]
            bot = nonebot.get_bot()
            msg = f"杂鱼cx啊，天天在群里水来水去，这样真的好吗？别总浪费时间在无意义的闲聊上了，你的题目还堆着一大堆呢！振作起来，把精力用在刀刃上，每天进步一点点，才能看到不一样的自己。别让懒惰成为你的标签，拿出行动来证明自己，给自己一个机会闪闪发光，不然你会后悔的喵！现在就关掉聊天窗口，拿起笔，认真解决几个问题，让自己离成功更近一步吧！\n新的cf题目已送达:{problem_list_name[choice_problem]} {problem_list_url[choice_problem]}"
            await bot.send_group_msg(group_id=867756249, message=msg)
            try:
                logger.debug(msg)
                problem_detail = await client.get(problem_list_url[choice_problem])
                problem_detail = problem_detail.text
                problem_detail_html = etree.HTML(problem_detail)
                problem_content = problem_detail_html.xpath('//*[@id="pageContent"]/div[3]/div[2]/div/div[2]//text()')
                problem_content = " ".join([s.strip() for s in problem_content])
                msg = f"题目大意:\n{problem_content}"
                await bot.send_group_msg(group_id=867756249, message=msg)
            except Exception as e:
                logger.debug(e)
            try:
                problem_function = problem_detail_html.xpath('//*[@id="sidebar"]/div[3]/div[2]/div/span/text()')
                problem_function.pop()
                problem_function = ",".join([s.strip() for s in problem_function])
                msg = f"题目标签:{problem_function}"
                await bot.send_group_msg(group_id=867756249, message=msg)
            except Exception as e:
                logger.debug(e)
            try:
                system = [
                    {"role": "system",
                     "content": "You are a professional, authentic translation engine. You only return the translated text, without any explanations."}
                ]
                conversation = [
                    {"role": "user",
                     "content": f"Please translate into chinese (avoid explaining the original text):\n{problem_content}"}
                ]
                openai_client = AsyncOpenAI(
                    api_key="sk-suVkkUhBvjhsONtr579c8923700248A89620CaA411Ce5bF9",
                    base_url="https://newapi.hxzzz.asia/v1",
                    max_retries=5,
                )
                problem_content_chinese = await openai_client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=system + conversation,
                )
                problem_content_chinese = problem_content_chinese.json()
                problem_content_chinese = json.loads(problem_content_chinese)
                logger.debug(problem_content_chinese['choices'][0]['message']['content'])
                msg = "中文题目大意:\n" + problem_content_chinese['choices'][0]['message']['content']
                await bot.send_group_msg(group_id=867756249, message=msg)
            except Exception as e:
                logger.debug(e)
        except Exception as e:
            logger.debug(e)
