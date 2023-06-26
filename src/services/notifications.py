import abc

import aiogram
import aiogram.utils.exceptions
import structlog
from aiogram import Bot
from aiogram.utils.exceptions import TelegramAPIError

import config
from config import AppSettings
from database import schemas

logger = structlog.get_logger('app')


class BaseNotification(abc.ABC):
    @abc.abstractmethod
    def send(self, *args):
        pass


class NewPurchaseNotification(BaseNotification):
    def __init__(self, bot: Bot, sale: schemas.Sale, payment_method: str,
                 product_name: str, product_units: list[schemas.ProductUnit]):
        self.__sale = sale
        self.__product_units = product_units
        self.__product_name = product_name
        self.__payment_method = payment_method
        self.__bot = bot

    async def send(self):
        text = self.__get_text()
        media_groups = []
        admins_id = AppSettings().admins_id
        for admin_id in admins_id:
            try:
                await self.__bot.send_message(admin_id, text)
            except TelegramAPIError:
                logger.warning(
                    'Could not send message: new purchase',
                    telegram_id=admin_id,
                )
        for i, unit in enumerate(unit for unit in self.__product_units if
                                 unit.type == 'document'):
            if i % 10 == 0:
                media_groups.append(aiogram.types.MediaGroup())
            path = config.PRODUCT_UNITS_PATH / unit.content
            media_groups[-1].attach_document(aiogram.types.InputFile(path))
        for admin_id in admins_id:
            try:
                for media_group in media_groups:
                    await self.__bot.send_media_group(admin_id, media_group)
            except (
                    aiogram.exceptions.BotBlocked,
                    aiogram.exceptions.ChatNotFound):
                continue

    def __get_text(self):
        text = (
                '🛒 New purchase\n'
                '➖➖➖➖➖➖➖➖➖➖\n'
                f'🆔 Order Number: {self.__sale.id}\n' +
                (
                    f'🙍‍♂ Customer: @{self.__sale.username}\n' if self.__sale.username is not None else '') +
                f'#️⃣ User ID: {self.__sale.user_id}\n'
                '➖➖➖➖➖➖➖➖➖➖\n'
                f'📙 Product Name: {self.__product_name}\n'
                f'📦 Quantity: {self.__sale.quantity} pc(s).\n'
                f'💰 Amount of purchase: ${self.__sale.amount}.\n'
                '➖➖➖➖➖➖➖➖➖➖\n'
                f'💳 Payment Method: {self.__payment_method}\n'
                '➖➖➖➖➖➖➖➖➖➖\n'
                '📱 Data:\n\n'
        )
        for product_unit in self.__product_units:
            if product_unit.type == 'text':
                text += f'{product_unit.content}\n'
        return text


class BalanceRefillNotification(BaseNotification):
    def __init__(self, bot: Bot, amount: float, user: schemas.User):
        self.__amount = amount
        self.__user = user
        self.__bot = bot

    async def send(self, *args):
        for admin_id in AppSettings().admins_id:
            try:
                await self.__bot.send_message(
                    admin_id,
                    f'✅ Balance was topped up by {self.__amount} by User: '
                    f'{"@" + self.__user.username if self.__user.username else self.__user.id}'
                )
            except (
                    aiogram.exceptions.BotBlocked,
                    aiogram.exceptions.ChatNotFound):
                continue


class ErrorNotification(BaseNotification):
    def __init__(self, bot: Bot, error_message: Exception):
        self.__error_message = error_message
        self.__bot = bot

    async def send(self):
        text = (
            f"❗ Error During Operation ❗\n"
            f"{self.__error_message}\n\n❗"
            f" The bot will restart automatically."
        )
        for user_id in AppSettings().admins_id:
            try:
                await self.__bot.send_message(user_id, text)
            except (
                    aiogram.exceptions.BotBlocked,
                    aiogram.exceptions.ChatNotFound):
                continue
