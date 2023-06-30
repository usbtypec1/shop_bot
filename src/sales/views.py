import aiogram
import aiogram.types
import aiogram.utils.exceptions
import structlog
from aiogram import Bot
from aiogram.utils.exceptions import TelegramAPIError

import config
from common.views import View
from config import AppSettings
from database import schemas
from keyboards.inline import payments_keyboards
from responses import base

logger = structlog.get_logger('app')


class NewPurchaseNotificationView(View):
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


class CoinbasePaymentLinkResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery, amount: float,
                 quantity: int, payment_url: str):
        self.__query = query
        self.__amount = amount
        self.__quantity = quantity
        self.__keyboard = payments_keyboards.CoinbasePaymentKeyboard(
            payment_url)

    async def _send_response(self):
        await self.__query.answer()
        await self.__query.message.edit_text(
            "<b>Currency</b>: USD\n"
            f"<b>Quantity</b>: {self.__quantity} pc(s).\n"
            f"<b>Amount: ${self.__amount}.</b>",
            reply_markup=self.__keyboard
        )


class PurchaseInformationResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery, sale_id: int,
                 product_name: str,
                 quantity: int, amount: float, product_units: list[
                schemas.ProductUnit]):
        self.__query = query
        self.__sale_id = sale_id
        self.__product_name = product_name
        self.__quantity = quantity
        self.__amount = amount
        self.__product_units = product_units

    async def _send_response(self):
        text = self.get_text()
        await self.__query.message.delete()
        await self.__query.message.answer(text)
        media_group = None
        is_media_group_sent = False
        for i, unit in enumerate(unit for unit in self.__product_units if
                                 unit.type == 'document'):
            if i % 10 == 0:
                is_media_group_sent = False
                if media_group is not None:
                    await self.__query.message.answer_media_group(media_group)
                    is_media_group_sent = True
                media_group = aiogram.types.MediaGroup()
            path = config.PRODUCT_UNITS_PATH / unit.content
            media_group.attach_document(aiogram.types.InputFile(path))
        if not is_media_group_sent and media_group is not None:
            await self.__query.message.answer_media_group(media_group)

    def get_text(self):
        text = (
            '🛒 Purchase Information\n'
            '➖➖➖➖➖➖➖➖➖➖\n'
            f'🆔 Order Number: {self.__sale_id}\n'
            '➖➖➖➖➖➖➖➖➖➖\n'
            f'📙 Product Name: {self.__product_name}\n'
            f'📦 Quantity: {self.__quantity} pc(s).\n'
            f'💰 Amount of purchase: ${self.__amount}.\n'
            '➖➖➖➖➖➖➖➖➖➖\n'
            '📱 Data:\n\n'
        )

        for product_unit in self.__product_units:
            if product_unit.type == 'text':
                text += f'{product_unit.content}\n'
        return text
