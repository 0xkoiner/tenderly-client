import random
import asyncio
import aiohttp
from loguru import logger
from typing import Optional
from datetime import datetime
from libs.py_eth_async.data.models import Networks, Union


class DateTimeConverter:
    @staticmethod
    async def to_unix(date_time_str: str) -> int:
        """
        Convert date and time string to Unix timestamp.

        :param date_time_str: str, date and time in the format 'dd/mm/yyyy - hh:mm'
        :return: int, Unix timestamp
        """
        date_time_format = '%d/%m/%Y - %H:%M'
        dt = datetime.strptime(date_time_str, date_time_format)
        unix_timestamp = int(dt.timestamp())
        return unix_timestamp

    @staticmethod
    async def from_unix(unix_timestamp: int) -> str:
        """
        Convert Unix timestamp to date and time string.

        :param unix_timestamp: int, Unix timestamp
        :return: str, date and time in the format 'dd/mm/yyyy - hh:mm'
        """
        dt = datetime.fromtimestamp(unix_timestamp)
        date_time_str = dt.strftime('%d/%m/%Y - %H:%M')
        return date_time_str


class Helper:
    @staticmethod
    async def get_network(network: str) -> Optional[Networks] or None:
        networks: dict = {
            'bsc': Networks.BSC,
            'fantom': Networks.Fantom,
            'polygon': Networks.Polygon,
            'ethereum': Networks.Ethereum,
            'avalanche': Networks.Avalanche,
        }

        return networks[network]

    @staticmethod
    async def get_next_action_time(now: int, settings, action: str, interval_in_day: int) -> int:
        day = 86400
        interval = random.randint(int(settings.next_action.from_), int(settings.next_action.to_))
        adjustment = random.choice([interval, -interval])

        if 'hatch' in action:
            return now + (day * interval_in_day) + adjustment
        if 'withdraw' in action:
            return now + (day * interval_in_day) + adjustment

    @staticmethod
    async def get_token_price(token_symbol='ETH', default_value=-1) -> Union[int, float]:
        token_symbol = token_symbol.upper()
        params = {
            'fsym': token_symbol,
            'tsyms': 'USD'
        }
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    logger.info(
                        f'Getting {token_symbol} price')
                    async with session.get(
                            f'https://min-api.cryptocompare.com/data/price', params=params,
                    ) as r:
                        result_dict = await r.json()
                        if 'HasWarning' in result_dict and not result_dict['HasWarning']:
                            logger.error(
                                f'Getting {token_symbol}'
                                f' price | {result_dict["Message"]}'
                            )
                            return default_value

                        return result_dict['USD']

            except Exception as e:
                logger.error(f'Getting {token_symbol} price: {e}')
                await asyncio.sleep(5)