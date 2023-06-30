import structlog
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, Message

from common.filters import AdminFilter
from common.views import answer_view
from mailing.services import send_mailing
from mailing.states import MailingStates
from mailing.views import MailingView, MailingFinishView
from users.repositories import UserRepository
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
        user_repository: UserRepository,
) -> None:
    await state.finish()
    telegram_ids = user_repository.get_all_telegram_ids()
    await message.answer('✅ The mailing has started')

    received_users_count = await send_mailing(message, telegram_ids)
    failed_newsletters_count = len(telegram_ids) - received_users_count

    view = MailingFinishView(
        successful_newsletters=received_users_count,
        unsuccessful_newsletters=failed_newsletters_count,
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
