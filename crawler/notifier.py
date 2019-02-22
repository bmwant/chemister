from http import HTTPStatus

import aiohttp

import settings
from utils import get_logger


logger = get_logger(__name__)

DOLLAR_ICON = '\U0001F4B5'
BANK_ICON = '\U0001F3E6'
TRADER_ICON = '\U0001F911'
ARROW_ICON = '\U000027A1'

def format_message(transaction_type, amount, rate, bank):
    today = datetime.date.today()
    icons = f'{ARROW_ICON}{BANK_ICON}' if transaction_type == 'sale' else f'{ARROW_ICON}{TRADER_ICON}'
    return (
        f'{icons}\nDate: {today}\n'
        f'Type: {transaction_type}\n'
        f'Amount: {amount}\n'
        f'Rate: {rate}\nBank: {bank}')


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
