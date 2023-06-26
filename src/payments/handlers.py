import structlog
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, Update

import config
import responses.payments_management
from common.filters import AdminFilter
from keyboards.inline import callback_factories
from mailing.states import ChangeCoinbaseData
from payments.exceptions import BalanceAmountValidatorError
from services.payments_apis import coinbase_api

logger = structlog.get_logger('app')


async def on_balance_amount_validation_error(
        update: Update,
        _: BalanceAmountValidatorError,
) -> bool:
    text = '❌ Incorrect balance amount!'
    if update.message is not None:
        await update.message.answer(text)
    if update.callback_query is not None:
        await update.callback_query.answer(text, show_alert=True)
    return True


async def payments_management(message: Message) -> None:
    await responses.payments_management.PaymentsManagementResponse(message)


async def coinbase_management(message: Message) -> None:
    await responses.payments_management.CoinbaseManagementResponse(message)


async def check_coinbase(query: CallbackQuery) -> None:
    if coinbase_api.CoinbaseAPI(config.CoinbaseSettings().api_key).check():
        await responses.payments_management.PaymentSystemIsValid(query)
    else:
        await responses.payments_management.PaymentSystemIsNotValid(query)


async def change_api_key(query: CallbackQuery) -> None:
    await responses.payments_management.ChangeCoinbaseAPIKeyResponse(query)
    await ChangeCoinbaseData.waiting_api_key.set()


async def change_api_key_input(
        message: Message,
        state: FSMContext,
) -> None:
    await state.finish()
    config.set_env_var('COINBASE_API_KEY', message.text)
    await responses.payments_management.SuccessChangingPaymentsData(message)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_errors_handler(
        on_balance_amount_validation_error,
        exception=BalanceAmountValidatorError,
    )
    dispatcher.register_message_handler(
        payments_management,
        Text('💳 Payment Management'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        coinbase_management,
        Text('🌐 Coinbase'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        check_coinbase,
        callback_factories.PaymentSystemCallbackFactory().filter(
            system='coinbase', action='check'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        change_api_key,
        callback_factories.PaymentSystemCallbackFactory().filter(
            system='coinbase', action='change_api_key'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        change_api_key_input,
        AdminFilter(),
        state=ChangeCoinbaseData.waiting_api_key,
    )
    logger.debug('Registered payments handlers')
