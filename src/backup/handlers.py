from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.types import Message
from apscheduler.schedulers.base import BaseScheduler

import config
from backup import tasks
from backup.states import BackupStates
from backup.views import (
    BackupView, BackupPeriodView, SendingBackupPeriodView,
    SuccessBackupSettingView
)
from common.filters import AdminFilter
from common.views import answer_view


async def backup(message: Message):
    await answer_view(message=message, view=BackupView())


async def manual_backup(_):
    tasks.make_database_backup()
    await tasks.send_database_backup_to_admin(config.BackupSettings().admin_id)


async def full_backup(_):
    admin_id = config.BackupSettings().admin_id
    tasks.make_database_backup()
    tasks.make_project_backup()
    await tasks.send_database_backup_to_admin(admin_id)
    await tasks.send_project_backup_to_admin(admin_id)


async def manage_backup_schedule(message: Message):
    await BackupStates.waiting_for_backup_period.set()
    await answer_view(message=message, view=BackupPeriodView())


async def backup_period_handler(message: Message, state: FSMContext):
    backup_periods = {
        '⏱ Every Hour': '0 */1 * * *',
        '⏱ Every Six Hours': '0 */6 * * *',
        '⏱ Every 24 Hours': '0 0 */1 * *'
    }
    backup_period = backup_periods.get(message.text, message.text)
    if tasks.check_period(backup_period):
        humanized_backup_period = (
            message.text.replace('⏱ ', '').lower()
            if message.text in backup_periods else ''
        )
        await answer_view(message=message, view=SendingBackupPeriodView())
        await state.update_data({
            'backup_period': backup_periods.get(message.text, message.text),
            'humanized_backup_period': humanized_backup_period
        })
        await BackupStates.next()
    else:
        await message.answer('❌ Invalid period')


async def sending_backup_period_handler(scheduler: BaseScheduler,
                                        message: Message, state: FSMContext):
    sending_backup_periods = {
        '⏱ Everyday': '0 0 */1 * *',
        '⏱ Every 3 Days': '0 0 */3 * *',
        '⏱ Every Week': '0 0 */7 * *'
    }
    data = await state.get_data()
    backup_period = data['backup_period']
    humanized_backup_period = data['humanized_backup_period']
    await state.finish()
    sending_backup_period = sending_backup_periods.get(message.text,
                                                       message.text)
    humanized_sending_backup_periods = (
        message.text.replace('⏱ ', '').lower()
        if message.text in sending_backup_periods else ''
    )
    if tasks.check_period(sending_backup_period):
        tasks.reschedule_task(scheduler, 'make_database_backup',
                              sending_backup_period)
        settings = config.TOMLSettings()
        tasks.reschedule_task(scheduler, 'send_database_backup_to_admin',
                              backup_period)
        settings['backup']['backup_period'] = backup_period
        settings['backup']['sending_backup_period'] = sending_backup_period
        settings.save()
        view = SuccessBackupSettingView(
            backup_period=humanized_backup_period,
            sending_backup_period=humanized_backup_period,
            backup_path=config.BACKUP_PATH,
        )
        await answer_view(message=message, view=view)
    else:
        await message.answer('❌ Invalid period')


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        backup,
        Text('💾 Backup'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        manual_backup,
        Text('📀 Manual Backup'),
        IDFilter(config.BackupSettings().admin_id),
        state='*',
    )
    dispatcher.register_message_handler(
        full_backup,
        Text('📲 Backup Full Shop'),
        IDFilter(config.BackupSettings().admin_id),
        state='*',
    )
    dispatcher.register_message_handler(
        manage_backup_schedule,
        Text('⏰ Manage Cron'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        backup_period_handler,
        AdminFilter(),
        state=BackupStates.waiting_for_backup_period,
    )
    dispatcher.register_message_handler(
        sending_backup_period_handler,
        AdminFilter(),
        state=BackupStates.waiting_for_sending_backup_period,
    )
