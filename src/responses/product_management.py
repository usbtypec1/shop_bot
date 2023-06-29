import aiogram
import structlog

import config
from database import schemas
from keyboards.inline import product_management_keyboards
from responses import base

logger = structlog.get_logger('app')


class ProductUnitsResponse(base.BaseResponse):
    def __init__(self,
                 update: aiogram.types.CallbackQuery | aiogram.types.Message,
                 category_id: int, product_id: int,
                 product_units: list[schemas.ProductUnit],
                 subcategory_id: int = None):
        self.__update = update
        self.__keyboard = product_management_keyboards.ProductUnitsKeyboard(
            category_id, product_id, product_units, subcategory_id
        )

    async def _send_response(self) -> aiogram.types.Message:
        message_text = '📦 All available data'
        if isinstance(self.__update, aiogram.types.CallbackQuery):
            await self.__update.answer()
            await self.__update.message.delete()
            return await self.__update.message.answer(message_text,
                                                      reply_markup=self.__keyboard)
        elif isinstance(self.__update, aiogram.types.Message):
            return await self.__update.answer(message_text,
                                              reply_markup=self.__keyboard)


class ProductUnitResponse(base.BaseResponse):
    def __init__(self,
                 update: aiogram.types.CallbackQuery | aiogram.types.Message,
                 product_id: int, product_unit: schemas.ProductUnit,
                 category_id: int, subcategory_id: int = None):
        self.__update = update
        self.__unit = product_unit
        self.__keyboard = product_management_keyboards.ProductUnitKeyboard(
            category_id, product_id, self.__unit.id, subcategory_id
        )

    async def _send_response(self):
        text = self.get_text()
        if isinstance(self.__update, aiogram.types.CallbackQuery):
            await self.__update.answer()
            if self.__unit.type == 'text':
                await self.__update.message.edit_text(
                    text, reply_markup=self.__keyboard
                )
            if self.__unit.type == 'document':
                await self.__update.message.delete()
                await self.__update.message.answer_document(
                    aiogram.types.InputFile(
                        config.PRODUCT_UNITS_PATH / self.__unit.content),
                    caption=text,
                    reply_markup=self.__keyboard
                )
        elif isinstance(self.__update, aiogram.types.Message):
            if self.__unit.type == 'text':
                await self.__update.answer(text, reply_markup=self.__keyboard)
            if self.__unit.type == 'document':
                await self.__update.answer_document(
                    aiogram.types.InputFile(
                        config.PRODUCT_UNITS_PATH / self.__unit.content),
                    caption=text, reply_markup=self.__keyboard
                )

    def get_text(self) -> str:
        if self.__unit.type == 'text':
            return (
                f'📋 Product Type: Text\n'
                f'📦 Data:\n\n{self.__unit.content}'
            )
        elif self.__unit.type == 'document':
            return f'📋 Product Type: Document\n'
        return ''
