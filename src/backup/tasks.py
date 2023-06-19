import os
import pathlib
import shutil
import tempfile
from collections.abc import Callable

from aiogram import Bot
from aiogram.types import InputFile
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

import config


def setup_tasks(scheduler: BaseScheduler):
    scheduler.start()
    backup_settings = config.BackupSettings()
    add_task(scheduler, make_database_backup,
             backup_settings.backup_period, 'make_database_backup')
    add_task(
        scheduler, send_database_backup_to_admin,
        backup_settings.sending_backup_period,
        'send_database_backup_to_admin', backup_settings.admin_id
    )


def check_period(period: str) -> bool:
    try:
        CronTrigger().from_crontab(period)
    except ValueError:
        return False
    return True


def add_task(
        scheduler: BaseScheduler,
        task: Callable,
        period: str,
        job_id: str,
        *task_args,
        **task_kwargs
):
    scheduler.add_job(
        task,
        CronTrigger().from_crontab(period),
        task_args,
        task_kwargs,
        id=job_id,
    )


def reschedule_task(
        scheduler: BaseScheduler,
        job_id: str,
        period: str,
):
    scheduler.reschedule_job(
        job_id=job_id,
        trigger=CronTrigger().from_crontab(period),
    )


async def send_project_backup_to_admin(bot: Bot, admin_id: int):
    backup_dir = config.BACKUP_PATH / 'project'
    file = shutil.make_archive(
        base_name=str(pathlib.Path(tempfile.mkdtemp()) / 'project'),
        format='zip', root_dir=backup_dir,
    )
    await bot.send_document(admin_id, InputFile(file))


async def send_database_backup_to_admin(bot: Bot, admin_id: int):
    backups = os.listdir(config.BACKUP_PATH / 'database')
    last_backup_id = int(backups[-1].replace('backup_', ''))
    backup_dir = config.BACKUP_PATH / 'database' / f'backup_{last_backup_id}'
    file = shutil.make_archive(
        str(pathlib.Path(tempfile.mkdtemp()) / 'database'), 'zip', backup_dir)
    await bot.send_document(admin_id, InputFile(file))


def make_project_backup():
    if not config.BACKUP_PATH.exists():
        config.BACKUP_PATH.mkdir()
    command = pathlib.Path.joinpath(
        pathlib.Path(os.path.abspath('..')),
        'scripts',
        'backup_project.sh',
    )
    os.system(command)


def make_database_backup():
    if not config.BACKUP_PATH.exists():
        config.BACKUP_PATH.mkdir()
    backup_dir = config.BACKUP_PATH / 'database'
    if not backup_dir.exists():
        backup_dir.mkdir()
    backups = os.listdir(backup_dir)
    for backup in backups[:-2]:
        shutil.rmtree(backup_dir / backup)
    last_backup_id = int(backups[-1].replace('backup_', '')) if backups else 0
    backup_dir = backup_dir / f'backup_{str(last_backup_id + 1)}'
    temp_dir = pathlib.Path(tempfile.mkdtemp())
    shutil.copytree(config.DATA_PATH / 'products', temp_dir / 'products')
    shutil.copy(config.DATA_PATH / 'database.db', temp_dir)
    shutil.move(temp_dir, backup_dir)
