from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ChatType

import config
import database
import responses.balance
import responses.payments
from database import queries
from keyboards.inline.callback_factories import TopUpBalanceCallbackFactory
from payments.states import TopUpBalance
from services import notifications
from services.payments_apis import coinbase_api
from users.exceptions import UserNotInDatabase


async def balance(message: Message) -> None:
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, message.from_user.id):
            raise UserNotInDatabase
        await responses.balance.BalanceResponse(
            message,
            queries.get_user(session, telegram_id=message.from_user.id).balance
        )


async def top_up_balance(
        query: CallbackQuery,
        callback_data: dict[str: str],
        state: FSMContext,
):
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise UserNotInDatabase
    await responses.balance.BalanceAmountResponse(query)
    await TopUpBalance.waiting_for_amount.set()
    await state.update_data({'callback_data': callback_data})


async def balance_amount(message: Message, state: FSMContext) -> None:
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, message.from_user.id):
            raise UserNotInDatabase
    if message.text.replace('.', '').isdigit() and '-' not in message.text:
        callback_data = (await state.get_data())['callback_data']
        callback_data['amount'] = message.text
        await state.finish()
        await responses.balance.PaymentMethodResponse(
            message, callback_data=callback_data,
            crypto_payments=config.PaymentsSettings().crypto_payments
        )
    else:
        await responses.balance.IncorrectBalanceAmountResponse(message)


async def top_up_balance_with_coinbase(
        query: CallbackQuery,
        callback_data: dict[str: str],
) -> None:
    with database.create_session() as session:
        user = queries.get_user(session, telegram_id=query.from_user.id)
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise UserNotInDatabase
        amount = float(callback_data['amount'])
        api = coinbase_api.CoinbaseAPI(config.CoinbaseSettings().api_key)
        charge = api.create_charge('Balance', amount)
        payments_message = await responses.payments.CoinbasePaymentBalanceResponse(
            query, amount, charge['hosted_url']
        )
        if await api.check_payment(charge):
            queries.top_up_balance(session, user.id, amount)
            await responses.balance.SuccessBalanceRefillResponse(query, amount)
            await notifications.BalanceRefillNotification(amount, user).send()
        else:
            try:
                amount = float(
                    charge['timeline'][-1]['payment']['value']['amount'])
            except KeyError:
                amount = 0
            if amount > 0:
                await responses.balance.SuccessBalanceRefillResponse(query,
                                                                     amount)
                await notifications.BalanceRefillNotification(amount,
                                                              user).send()
            else:
                await responses.balance.FailedBalanceRefillResponse(
                    payments_message)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        balance,
        Text('💲 Balance'),
    )
    dispatcher.register_callback_query_handler(
        top_up_balance,
        TopUpBalanceCallbackFactory().filter(amount='', payment_method=''),
        state='*',
    )
    dispatcher.register_message_handler(
        balance_amount,
        state=TopUpBalance.waiting_for_amount,
    )
    dispatcher.register_callback_query_handler(
        top_up_balance_with_coinbase,
        TopUpBalanceCallbackFactory().filter(payment_method='coinbase'),
        chat_type=ChatType.PRIVATE,
    )
