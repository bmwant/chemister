from datetime import datetime
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
    today = datetime.now()
    icons = f'{ARROW_ICON}{BANK_ICON}' \
        if transaction_type == 'sale' \
        else f'{ARROW_ICON}{TRADER_ICON}'
    total = amount * rate
    date = today.strftime(settings.DEFAULT_DATETIME_FORMAT)
    return (
        f'{icons}\n'
        f'Date: {date}\n'
        f'Type: {transaction_type}\n'
        f'Amount: {amount} $\n'
        f'Rate: {rate}\n'
        f'Total: {total} UAH\n'
        f'Bank: {bank}\n'
    )


async def notify(message):
    url = settings.ENDPOINT_TEMPLATE.format(bot_api_key=settings.TELEGRAM_BOT_TOKEN)
    if settings.TELEGRAM_BOT_TOKEN is None or settings.CHAT_ID is None:
        logger.warning(
            'Not sending notifications to telegram. '
            'Make sure TELEGRAM_BOT_TOKEN and CHAT_ID are set.'
        )
        return

    params = {
        'chat_id': settings.CHAT_ID,
        'text': message,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != HTTPStatus.OK:
                text = await resp.text()
                logger.error(f'Error {resp.status}: {text}')
