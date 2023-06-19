from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = ('BackupStates',)


class BackupStates(StatesGroup):
    waiting_for_backup_period = State()
    waiting_for_sending_backup_period = State()
