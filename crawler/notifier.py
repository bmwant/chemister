from http import HTTPStatus

import aiohttp

import settings
from utils import get_logger


logger = get_logger(__name__)


async def notify(message):
    url = settings.ENDPOINT_TEMPLATE.format(bot_api_key=settings.TELEGRAM_BOT_TOKEN)
    params = {
        'chat_id': settings.CHAT_ID,
        'text': message,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != HTTPStatus.OK:
                text = await resp.text()
                logger.error(f'Error {resp.status}: {text}')
