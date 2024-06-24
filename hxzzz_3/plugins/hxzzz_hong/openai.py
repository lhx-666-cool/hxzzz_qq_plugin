import random
from typing import Any, Tuple
import httpx
from nonebot import logger
from openai import AsyncOpenAI


def remove_punctuation(text):
    import string
    for i in range(len(text)):
        if text[i] not in string.punctuation:
            return text[i:]
    return ""


async def get_chat_response(preset: str, conversation: list, msg: str) -> Tuple[Any, bool]:
    openai_client = AsyncOpenAI(
        api_key="sk-D44S9HD3jbnyO2cL87Ce77D5F437433f8f8073475999D06a",
        base_url="https://newapi.hxzzz.asia/v1",
        max_retries=3,
    )
    """
    :param proxy: 代理
    :param key: 密钥
    :param preset: 人格
    :param conversation: 历史会话
    :param msg: 消息内容
    :return:
    """
    system = [
        {"role": "system", "content": preset}
    ]
    prompt = {"role": "user", "content": msg}
    conversation.append(prompt)
    try:
        response = await openai_client.chat.completions.create(
            model="65a232c082ff90a2ad2f15e2",
            messages=system + conversation,
            stream=True,
        )
        logger.debug(response)
        message = ""
        async for chunk in response:
            logger.debug(chunk)
            message += chunk.choices[0].delta.content or ""
        logger.debug(message)
        logger.debug("ok")
        try:
            response = {'id': 'chatcmpl-9CQfRkPbKqNNqdwbi6CgLqNLO0nhe', 'object': 'chat.completion',
                        'created': 1712749473, 'model': 'gpt-4-0125-preview', 'choices': [
                    {'index': 0, 'message': {'role': 'assistant', 'content': message}, 'finish_reason': 'stop'}],
                        'usage': {'prompt_tokens': 300, 'completion_tokens': len(message) * 2,
                                  'total_tokens': 3 == + len(message) * 2}}
            res: str = remove_punctuation(response['choices'][0]['message']['content'].strip())
            conversation.append({"role": "assistant", "content": res})

            return response, True
        except:
            return response, False
    except httpx.ConnectTimeout as e:
        return f"发生HTTP超时错误: {e.request.url}", False
    except Exception as e:
        return f"发生未知错误: {type(e)} {e}", False

