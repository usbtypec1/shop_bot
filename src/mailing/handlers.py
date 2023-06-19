import structlog
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, Message

import database
from common.filters import AdminFilter
from common.views import answer_view
from database import queries
from mailing.exceptions import SendMailError
from mailing.states import MailingStates
from mailing.views import MailingView, MailingFinishView
from users.views import AdminMenuView

logger = structlog.get_logger('app')


async def on_show_newsletter_menu(message: Message) -> None:
    await answer_view(message=message, view=MailingView())


async def create_newsletter(message: Message) -> None:
    await MailingStates.waiting_newsletter.set()
    await message.answer(
        '✏️ Enter the text of your newsletter in the usual telegram format'
        '\nOr attach a photo,'
        ' and specify the text in the description to the picture'
    )


async def send_newsletter(
        message: Message,
        state: FSMContext,
) -> None:
    await state.finish()
    with database.create_session() as session:
        users_id = queries.get_users_telegram_id(session)
    await message.answer('✅ The mailing has started')
    successfully_newsletters = unsuccessfully_newsletters = 0
    for user_id in users_id:
        try:
            try:
                await message.copy_to(user_id)
            except Exception:
                raise SendMailError
        except SendMailError:
            unsuccessfully_newsletters += 1
        else:
            successfully_newsletters += 1
    view = MailingFinishView(
        successful_newsletters=successfully_newsletters,
        unsuccessful_newsletters=unsuccessfully_newsletters,
    )
    await answer_view(message=message, view=view)
    await answer_view(message=message, view=AdminMenuView())


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_newsletter_menu,
        Text('📧 Newsletter'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        create_newsletter,
        Text('📮 Create Newsletter'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        send_newsletter,
        AdminFilter(),
        content_types=ContentType.ANY,
        state=MailingStates.waiting_newsletter,
    )
    logger.debug('Registered mailing handlers')
