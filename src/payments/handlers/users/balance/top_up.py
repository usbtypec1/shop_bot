from decimal import Decimal

import structlog
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, ChatType
from structlog.stdlib import BoundLogger

from common.services import AdminsNotificator
from common.views import answer_view, edit_message_by_view
from payments.services import parse_balance_amount
from payments.states import UserBalanceTopUpStates
from payments.views import (
    UserBalanceTopUpPaymentMethodsView,
    UserBalanceTopUpInvoiceView,
    UserBalanceTopUpNotificationView,
)
from payments.services.payments_apis import CoinbaseAPI
from top_up_bonuses.exceptions import TopUpBonusDoesNotExistError
from top_up_bonuses.repositories import TopUpBonusRepository
from top_up_bonuses.services import calculate_amount_to_top_up_with_bonus
from users.repositories import UserRepository

__all__ = ('register_handlers',)

logger: BoundLogger = structlog.get_logger('app')


async def on_start_balance_top_up_flow(
        callback_query: CallbackQuery,
):
    await UserBalanceTopUpStates.amount.set()
    await callback_query.message.edit_text('🔢 Enter amount')


async def on_balance_amount_to_top_up_input(
        message: Message,
        state: FSMContext,
) -> None:
    amount = parse_balance_amount(message.text)
    await UserBalanceTopUpStates.payment_method.set()
    await state.update_data(amount=amount)
    view = UserBalanceTopUpPaymentMethodsView()
    await answer_view(message=message, view=view)


async def top_up_balance_with_coinbase(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_repository: UserRepository,
        top_up_bonus_repository: TopUpBonusRepository,
        coinbase_api: CoinbaseAPI,
        admins_notificator: AdminsNotificator,
) -> None:
    state_data = await state.get_data()
    amount: Decimal = state_data['amount']

    user = user_repository.get_by_telegram_id(callback_query.from_user.id)
    charge = await coinbase_api.create_charge('Balance', amount)
    view = UserBalanceTopUpInvoiceView(
        amount_to_top_up=amount,
        hosted_url=charge['hosted_url'],
    )
    await edit_message_by_view(message=callback_query.message, view=view)

    if not await coinbase_api.check_payment(charge):
        try:
            amount = Decimal(
                charge['timeline'][-1]['payment']['value']['amount'])
        except KeyError:
            amount = Decimal('0')

        if amount <= 0:
            await callback_query.message.answer('🚫 Balance refill failed')
            return

    try:
        top_up_bonus = top_up_bonus_repository.get_by_top_up_amount(amount)
    except TopUpBonusDoesNotExistError:
        top_up_bonus_percentage = 0
    else:
        top_up_bonus_percentage = top_up_bonus.bonus_percentage
        logger.debug(
            'Top up bonus has been applied to balance top up',
            top_up_bonus_percentage=top_up_bonus_percentage,
        )

    amount_to_top_up_with_bonus = calculate_amount_to_top_up_with_bonus(
        amount_to_top_up=amount,
        bonus_percentage=top_up_bonus_percentage
    )
    user_repository.top_up_balance(
        user_id=user.id,
        amount_to_top_up=amount_to_top_up_with_bonus,
    )
    await callback_query.message.delete()
    await callback_query.message.answer(
        f'✅ Balance was topped up by {amount:.2f}'
    )
    view = UserBalanceTopUpNotificationView(
        amount=amount,
        username=user.username,
        user_telegram_id=user.telegram_id,
    )
    await admins_notificator.notify(
        text=view.get_text(),
        reply_markup=view.get_reply_markup(),
    )


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_balance_top_up_flow,
        Text('start-balance-top-up-flow'),
        state='*',
    )
    dispatcher.register_message_handler(
        on_balance_amount_to_top_up_input,
        chat_type=ChatType.PRIVATE,
        state=UserBalanceTopUpStates.amount,
    )
    dispatcher.register_callback_query_handler(
        top_up_balance_with_coinbase,
        Text('coinbase'),
        chat_type=ChatType.PRIVATE,
        state=UserBalanceTopUpStates.payment_method,
    )
