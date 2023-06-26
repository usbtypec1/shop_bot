import aiogram
import structlog

import config
import keyboards.reply.product_management_keyboards
from database import schemas
from keyboards.inline import product_management_keyboards
from keyboards.reply import shop_management_keyboards
from products.models import Product
from responses import base

logger = structlog.get_logger('responses')


class AddProductUnitResponse(base.BaseResponse):
    def __init__(self,
                 update: aiogram.types.Message | aiogram.types.CallbackQuery):
        self.__update = update
        self.__keyboard = keyboards.reply.product_management_keyboards.CompleteProductAddingKeyboard()

    async def _send_response(self):
        message_text = (
            '📦 Enter the product data\n\n'
            'Examples of download:\n\n'
            'Product 1\n'
            'Product 2\n'
            'Product n\n\n'
            'Grouped Documents\n\n'
            'The products will be loaded until you click ✅ Complete'
        )
        if isinstance(self.__update, aiogram.types.CallbackQuery):
            await self.__update.answer()
            await self.__update.message.delete()
            await self.__update.message.answer(message_text,
                                               reply_markup=self.__keyboard)
        elif isinstance(self.__update, aiogram.types.Message):
            await self.__update.answer(message_text,
                                       reply_markup=self.__keyboard)


class SuccessUnitAddingResponse(base.BaseResponse):
    def __init__(self, message: aiogram.types.Message):
        self.__message = message

    async def _send_response(self):
        await self.__message.answer('✅ Goods loaded')


class CompleteUnitLoadingResponse(base.BaseResponse):
    def __init__(self, message: aiogram.types.Message, product_name: str):
        self.__message = message
        self.__product_name = product_name
        self.__keyboard = keyboards.reply.shop_management_keyboards.ShopManagementKeyboard()

    async def _send_response(self):
        await self.__message.answer(
            f'✅ loading {self.__product_name} Completed',
            reply_markup=self.__keyboard
        )


class ProductResponse(base.BaseResponse):

    def __init__(
            self,
            update: aiogram.types.CallbackQuery | aiogram.types.Message,
            product: Product,
            category_id: int,
            subcategory_id: int | None = None,
    ):
        self.__update = update
        self.__product = product
        self.__keyboard = product_management_keyboards.ProductKeyboard(
            category_id, product.id, subcategory_id=subcategory_id
        )

    async def _send_response(self):
        message_text = (
            f'📓 Name: {self.__product.name}\n\n'
            f'📋 Description:\n\n{self.__product.description}\n\n'
            f'💳 Price: ${self.__product.price:.2f}\n\n'
            f'📦 Available to purchase: {self.__product.quantity}'
            f' pc{"s" if self.__product.quantity > 1 else ""}\n\n'
        )
        logger.debug('Product edit', product=self.__product)
        if isinstance(self.__update, aiogram.types.CallbackQuery):
            message = self.__update.message
        else:
            message = self.__update
        if not self.__product.picture:
            await message.answer(
                text=message_text,
                reply_markup=self.__keyboard,
            )
        elif len(self.__product.media_file_names) == 1:
            await answer_media_with_text(
                message=message,
                base_path=config.PRODUCT_PICTURE_PATH,
                product=self.__product,
                caption=message_text,
                reply_markup=self.__keyboard
            )
        else:
            await answer_medias(
                message=message,
                base_path=config.PRODUCT_PICTURE_PATH,
                product=self.__product,
            )
            await message.answer(
                text=message_text,
                reply_markup=self.__keyboard
            )


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


class EditProductUnitsResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery):
        self.__query = query

    async def _send_response(self):
        await self.__query.answer()
        await self.__query.message.edit_text(
            '📝 Enter the new product data, or Load file.')


class SuccessRemovalUnitResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery):
        self.__query = query

    async def _send_response(self) -> aiogram.types.Message:
        await self.__query.answer()
        return await self.__query.message.answer('✅ Position removed')
