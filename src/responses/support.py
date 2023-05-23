import aiogram.types

from keyboards.reply import support_keybords
from responses import base
from services.db_api import schemas


class UserSupportRequestsResponse(base.BaseResponse):
    def __init__(self,
                 update: aiogram.types.Message | aiogram.types.CallbackQuery,
                 support_requests: list[schemas.SupportTicket]):
        self.__update = update
        self.__keyboard = support_keybords.SupportRequestsKeyboard(
            support_requests, user_id=self.__update.from_user.id)

    async def _send_response(self):
        if isinstance(self.__update, aiogram.types.Message):
            await self.__update.answer('📚 My Support Requests',
                                       reply_markup=self.__keyboard)


class SupportRequestResponse(base.BaseResponse):
    def __init__(self, query: aiogram.types.CallbackQuery,
                 support_request: schemas.SupportTicket,
                 is_open: bool = None, user_id: int = None):
        self.__query = query
        self.__request = support_request
        self.__keyboard = support_keybords.SupportRequestMenuKeyboard(
            support_request.id, is_open, user_id)

    async def _send_response(self):
        await self.__query.answer()
        await self.__query.message.edit_text(
            (f'🆔 Request number: {self.__request.id}\n'
             '➖➖➖➖➖➖➖➖➖➖\n'
             f'📗 Request Subject: {self.__request.subject.name}\n'
             '📋 Description:\n'
             f'{self.__request.issue}\n'
             '➖➖➖➖➖➖➖➖➖➖\n'
             f'📱 Status: {"✅ Active" if self.__request.is_open else "❌ Closed"}' +
             (
                 '\n➖➖➖➖➖➖➖➖➖➖\n'
                 '📧 Answer:\n\n'
                 f'{self.__request.answer}' if not self.__request.is_open else ""
             )),
            reply_markup=self.__keyboard
        )
