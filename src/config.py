import collections
import os
import pathlib
from typing import Literal

import dotenv
import toml
from pydantic import BaseSettings, Field

# ROOT_DIR = pathlib.Path(os.path.abspath('__file__'))
ROOT_DIR = pathlib.Path(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)
# ROOT_DIR = '/root/shop_bot'
print(pathlib.Path(ROOT_DIR))
DATA_PATH = ROOT_DIR / 'data'
BACKUP_PATH = ROOT_DIR / 'backups'
PRODUCT_PATH = DATA_PATH / 'products'
PRODUCT_PICTURE_PATH = PRODUCT_PATH / 'pictures'
PRODUCT_UNITS_PATH = PRODUCT_PATH / 'units'
PENDING_DIR_PATH = DATA_PATH / 'pending'
SRC_PATH = ROOT_DIR / 'src'

dotenv.load_dotenv()


def set_env_var(key: str, value: str) -> None:
    dotenv_file = dotenv.find_dotenv()
    dotenv.set_key(dotenv_file, key, value, quote_mode="never")
    dotenv.load_dotenv()


class TOMLSettings(collections.UserDict):
    # SETTINGS_PATH = pathlib.Path(os.curdir) / 'settings.toml'
    SETTINGS_PATH = ROOT_DIR / 'src' / 'settings.toml'

    # SETTINGS_PATH = SRC_PATH + '/settings.toml'

    def __init__(self):
        super().__init__()
        settings_file = open(self.SETTINGS_PATH, 'r')
        self.update(toml.load(settings_file))

    def save(self):
        settings_file = open(self.SETTINGS_PATH, 'w')
        toml.dump(self, settings_file)


class AppSettings(BaseSettings):
    bot_token: str = Field(env='BOT_TOKEN')
    admins_id: list[int] = Field(env='ADMINS_ID', default_factory=list)
    debug: bool = Field(env='DEBUG', default=False)


class PaymentsSettings(BaseSettings):
    crypto_payments: str = TOMLSettings()['payments']['crypto_payments']


class QIWISettings(BaseSettings):
    payment_method: Literal['nickname', 'number'] = (
        TOMLSettings()['payments']['qiwi']['payment_method']
    )
    is_enabled: bool = TOMLSettings()['payments']['qiwi']['is_enabled']
    number: str = Field(None, env='QIWI_NUMBER')
    nickname: str = Field(None, env='QIWI_NICKNAME')
    token: str = Field(None, env='QIWI_TOKEN')


class YooMoneySettings(BaseSettings):
    __slots__ = ()
    number: str = Field(None, env='YOOMONEY_NUMBER')
    is_enabled: bool = TOMLSettings()['payments']['yoomoney']['is_enabled']
    token: str = Field(None, env='YOOMONEY_TOKEN')


class MinerlockSettings(BaseSettings):
    __slots__ = ()
    is_enabled: bool = TOMLSettings()['payments']['minerlock']['is_enabled']
    api_id: int = Field(None, env='MINERLOCK_API_ID')
    api_key: str = Field(None, env='MINERLOCK_API_KEY')


class CoinpaymentsSettings(BaseSettings):
    __slots__ = ()
    is_enabled: bool = TOMLSettings()['payments']['coinpayments']['is_enabled']
    public_key: str = Field(None, env='COINPAYMENTS_PUBLIC_KEY')
    secret_key: str = Field(None, env='COINPAYMENTS_SECRET_KEY')


class CoinbaseSettings(BaseSettings):
    __slots__ = ()
    is_enabled: bool = TOMLSettings()['payments']['coinbase']['is_enabled']
    api_key: str = Field(None, env='COINBASE_API_KEY')


class BackupSettings(BaseSettings):
    __slots__ = ()
    backup_period: str = TOMLSettings()['backup']['backup_period']
    sending_backup_period: str = TOMLSettings()['backup'][
        'sending_backup_period']
    admin_id: int = Field(None, env='ADMIN_ID_FOR_BACKUP_SENDING')


# used for extra text on certain categories, do NOT remove
class CustomCategoryMessages(BaseSettings):
    __slots__ = ()
    category1: str = Field(None, env='CATEGORY1')
    category2: str = Field(None, env='CATEGORY2')
    category3: str = Field(None, env='CATEGORY3')
