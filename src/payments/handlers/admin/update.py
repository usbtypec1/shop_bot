from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ChatType

import config
from common.filters import AdminFilter
from payments.callback_data import PaymentSystemCredentialsUpdateCallbackData
from payments.states import CoinbaseCredentialsUpdateStates
from services.payments_apis import CoinbaseAPI

__all__ = ('register_handlers',)


async def on_ask_new_coinbase_api_key(callback_query: CallbackQuery) -> None:
    await CoinbaseCredentialsUpdateStates.api_key.set()
    await callback_query.message.edit_text('🔑 Enter api key')


async def on_new_coinbase_api_key_input(
        message: Message,
        state: FSMContext,

) -> None:
    await state.finish()
    new_api_key = message.text
    coinbase_api = CoinbaseAPI(new_api_key)
    is_valid = coinbase_api.check()
    if not is_valid:
        await message.answer('❌ Invalid api key')
        return
    config.set_env_var('COINBASE_API_KEY', message.text)
    await message.answer('✅ Success! Data has been changed.')


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_ask_new_coinbase_api_key,
        AdminFilter(),
        PaymentSystemCredentialsUpdateCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_new_coinbase_api_key_input,
        AdminFilter(),
        chat_type=ChatType.PRIVATE,
        state=CoinbaseCredentialsUpdateStates.api_key,
    )
