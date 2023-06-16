from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from common.views import View

__all__ = (
    'BackupView',
    'BackupPeriodView',
    'SendingBackupPeriodView',
    'SuccessBackupSettingView',
)


class BackupView(View):
    text = '💾 Backup'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('📀 Manual Backup'),
                KeyboardButton('📲 Backup Full Shop'),
                KeyboardButton('⏰ Manage Cron'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )


class BackupPeriodView(View):
    text = (
        'Please enter how often you want the backups to be taken'
        '\n\n<i>You can send your own period with cron notation.</i>'
    )
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('⏱ Every Hour'),
                KeyboardButton('⏱ Every Six Hours'),
                KeyboardButton('⏱ Every 24 Hours'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )


class SendingBackupPeriodView(View):
    text = (
        'Please enter how often you want to send'
        ' backups to admin with .ZIP file'
        '\n\n<i>You can send your own period with cron notation.</i>',
    )
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('⏱ Everyday'),
                KeyboardButton('⏱ Every 3 Days'),
                KeyboardButton('⏱ Every Week'),
            ],
        ],
    )


class SuccessBackupSettingView(View):

    def __init__(
            self,
            *,
            backup_period: str,
            sending_backup_period: str,
            backup_path: str,
    ):
        self.__backup_period = backup_period
        self.__sending_backup_period = sending_backup_period
        self.__backup_path = backup_path

    def get_text(self) -> str:
        return (
            f'✅ The database will be backed up {self.__backup_period} '
            f'and saved in <code>{self.__backup_path}</code> '
            f'on the server, and ZIP file will be auto sent'
            f' to admin {self.__sending_backup_period}'
        )
