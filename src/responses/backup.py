from aiogram.types import Message

from keyboards.reply import backup_keyboards
from responses.base import BaseResponse


class BackupResponse(BaseResponse):
    def __init__(self, message: Message):
        self.__message = message
        self.__keyboard = backup_keyboards.BackupKeyboard()

    async def _send_response(self):
        await self.__message.answer('💾 Backup', reply_markup=self.__keyboard)


class BackupPeriodResponse(BaseResponse):
    def __init__(self, message: Message):
        self.__message = message
        self.__keyboard = backup_keyboards.BackupPeriodKeyboard()

    async def _send_response(self):
        await self.__message.answer(
            'Please enter how often you want the backups to be taken\n\n'
            '<i>You can send your own period with cron notation.</i>',
            reply_markup=self.__keyboard
        )


class SendingBackupPeriodResponse(BaseResponse):
    def __init__(self, message: Message):
        self.__message = message
        self.__keyboard = backup_keyboards.SendingBackupPeriodKeyboard()

    async def _send_response(self):
        await self.__message.answer(
            'Please enter how often you want to send'
            ' backups to admin with .ZIP file\n\n'
            '<i>You can send your own period with cron notation.</i>',
            reply_markup=self.__keyboard
        )


class SuccessBackupSettingResponse(BaseResponse):
    def __init__(
            self,
            message: Message,
            backup_period: str,
            sending_backup_period: str,
            backup_path: str,
    ):
        self.__message = message
        self.__backup_period = backup_period
        self.__sending_backup_period = sending_backup_period
        self.__backup_path = backup_path

    async def _send_response(self):
        await self.__message.answer(
            f'✅ The database will be backed up {self.__backup_period} '
            f'and saved in <code>{self.__backup_path}</code> '
            f'on the server, and ZIP file will be auto sent'
            f' to admin {self.__sending_backup_period}'
        )


class InvalidPeriodResponse(BaseResponse):
    def __init__(self, message: Message):
        self.__message = message

    async def _send_response(self):
        await self.__message.answer('❌ Invalid period')
