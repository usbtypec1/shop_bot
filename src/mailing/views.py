from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from common.views import View

__all__ = (
    'MailingView',
    'MailingFinishView',
)


class MailingView(View):
    text = '📧 Newsletter'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('📮 Create Newsletter'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )


class MailingFinishView(View):

    def __init__(
            self,
            *,
            successful_newsletters: int,
            unsuccessful_newsletters: int,
    ):
        self.__unsuccessful_newsletters = unsuccessful_newsletters
        self.__successful_newsletters = successful_newsletters

    def get_text(self) -> str:
        total_sent = (
                self.__unsuccessful_newsletters + self.__successful_newsletters
        )
        return (
            '✅ The newsletter is completed\n'
            f'Total sent: {total_sent}\n\n'
            f'✅ Successful: {self.__successful_newsletters}\n'
            f'❌ Not sent: {self.__unsuccessful_newsletters}'
        )
