import asyncio

import aiogram
from aiogram import dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from filters import is_admin
from filters.is_admin import IsUserAdmin
from keyboards.inline.callback_factories import (
    CategoryCallbackFactory,
    CategoriesCallbackFactory,
)
from loader import dp
from repositories.database import CategoryRepository, SubcategoryRepository
from responses.category_management import (
    CategoriesResponse,
    CategoryMenuResponse,
)
from services import db_api
from services.db_api import queries
from services.db_api.session import session_factory
from states import category_states
from states.category_states import (
    EditSubcategories,
    DeleteSubcategoryConfirm,
    DeleteConfirm,
)


@dp.callback_query_handler(
    CategoriesCallbackFactory().filter(action='manage'),
    is_admin.IsUserAdmin())
async def categories(query: aiogram.types.CallbackQuery):
    with db_api.create_session() as session:
        await CategoriesResponse(
            query, queries.get_all_categories(session)
        )


@dp.callback_query_handler(
    CategoryCallbackFactory().filter(action='manage', subcategory_id=''),
    is_admin.IsUserAdmin(),
)
async def category_menu(
        query: CallbackQuery,
        callback_data: dict[str, str],
):
    category_id = int(callback_data['category_id'])
    category_repository = CategoryRepository(session_factory)
    subcategory_repository = SubcategoryRepository(session_factory)

    category = category_repository.get_by_id(category_id)
    subcategories = subcategory_repository.get_by_category_id(category_id)

    await CategoryMenuResponse(
        update=query,
        category=category,
        subcategories=subcategories,
    )


@dp.message_handler(
    is_admin.IsUserAdmin(),
    state=category_states.EditSubcategories.waiting_subcategory_id,
)
async def edit_subcategory(
        message: Message,
        state: FSMContext,
):
    try:
        subcategory_id = int(message.text.strip())
    except ValueError:
        await message.reply(
            "⚠️ Please enter a valid integer ID for the subcategory.")
        return

    with db_api.create_session() as session:
        subcategory = queries.get_subcategory(session, subcategory_id)
        if not subcategory:
            await message.reply(
                f"⚠️ No subcategory found with ID {subcategory_id}."
                f" Please provide a valid ID."
            )
            return
        await state.update_data(subcategory_id=subcategory_id,
                                category_id=subcategory.category_id)
        await message.reply(
            f'✏️ Enter the new name for Subcategory {subcategory_id}:'
            f' {subcategory.name}'
        )
    await category_states.EditSubcategories.waiting_new_subcategory_name.set()


@dp.message_handler(
    IsUserAdmin(),
    state=EditSubcategories.waiting_new_subcategory_name,
)
async def edit_subcategory_name(
        message: aiogram.types.Message,
        state: dispatcher.FSMContext,
):
    new_subcategory_name = message.text.strip()
    if not new_subcategory_name:
        await message.reply(
            "⚠️ The subcategory name can't be empty."
            " Please provide a valid name."
        )
        return

    async with state.proxy() as data:
        subcategory_id = data.get('subcategory_id')
        category_id = data.get('category_id')

    if subcategory_id is None or category_id is None:
        await message.reply(
            "⚠️ The process has been interrupted. Please start over.")
        await state.finish()
        return

    with db_api.create_session() as session:
        queries.edit_subcategory(session, subcategory_id, new_subcategory_name)
        session.commit()

    await state.finish()

    await message.answer(
        f'✅ Subcategory {subcategory_id} updated to: {new_subcategory_name}')

    with db_api.create_session() as session:
        await CategoryMenuResponse(
            message, category_id,
            queries.get_category(session, category_id).name,
            queries.get_subcategories(session, category_id)
        )


@dp.message_handler(
    is_admin.IsUserAdmin(),
    state=category_states.DeleteConfirm.waiting_for_delete_category_confirm,
)
async def process_delete_category_confirm(
        message: aiogram.types.Message,
        state: dispatcher.FSMContext,
):
    state_data = await state.get_data()
    category_id = state_data['category_id']
    if message.text.lower() == 'yes':
        with db_api.create_session() as session:
            subcategories = queries.get_subcategories(session, int(category_id))
            if not subcategories:  # if no subcategories exist for this category
                queries.delete_category(session, int(category_id))
                await message.reply('✅ Category Removed')
            else:
                await message.reply(
                    '🛑🛑 Category contains subcategories. '
                    'Please delete them first.')
        with db_api.create_session() as session:
            await CategoriesResponse(
                message, queries.get_all_categories(session)
            )
    elif message.text.lower() == 'cancel':
        with db_api.create_session() as session:
            category = queries.get_category(session, category_id)
            category_name = category.name
            subcategories = queries.get_subcategories(session, category_id)
        await CategoryMenuResponse(
            message, category_id, category_name, subcategories
        )
    else:
        await message.reply('⚠️ Invalid input. Please type yes or cancel.')
    await state.finish()


@dp.callback_query_handler(
    CategoryCallbackFactory().filter(
        action='delete_subcategories',
        subcategory_id='',
    ),
    is_admin.IsUserAdmin(),
)
async def delete_subcategory(
        query: CallbackQuery,
        callback_data: dict[str, str],
        state: FSMContext,
):
    category_id = int(callback_data['category_id'])

    with db_api.create_session() as session:
        # Check if there are any subcategories in the category
        subcategories = queries.get_subcategories(session, category_id)
        if not subcategories:
            await query.message.answer(
                "⚠️ There are no subcategories under this category to delete.")
            await CategoryMenuResponse(
                update=query.message,
                category_id=category_id,
                category_name=queries.get_category(session, category_id).name,
                subcategories=subcategories,
            )
            return

    await state.set_data({'category_id': category_id})
    await DeleteSubcategoryConfirm.waiting_for_delete_subcategory_id.set()
    await query.message.reply(
        '🔢 Enter the ID of the subcategory to delete'
        '(after the (ID:) in the above list):'
    )


@dp.message_handler(
    is_admin.IsUserAdmin(),
    state=DeleteSubcategoryConfirm.waiting_for_delete_subcategory_id
)
async def process_delete_subcategory_id(
        message: aiogram.types.Message,
        state: dispatcher.FSMContext):
    subcategory_id = message.text
    state_data = await state.get_data()
    category_id = state_data['category_id']
    if subcategory_id.isdigit():
        with db_api.create_session() as session:
            subcategory = queries.get_subcategory(session, int(subcategory_id))
            if subcategory:
                await state.update_data(
                    subcategory_id=int(subcategory_id),
                    category_id=category_id,
                )
                await DeleteConfirm.waiting_for_delete_subcategory_confirm.set()
                await message.reply(
                    f"You have selected:\n Subcategory ID: {subcategory_id}"
                    f" - {subcategory.name}\n\n❓ "
                    f"Are you sure you want to delete it? Type yes or cancel.")
            else:
                await message.reply(
                    f'⚠️ No subcategory found with ID {subcategory_id}.')
    else:
        await message.reply(
            f'⚠️ Invalid subcategory ID. Please provide a valid ID.')


@dp.message_handler(
    IsUserAdmin(),
    state=DeleteConfirm.waiting_for_delete_subcategory_confirm,
)
async def process_delete_subcategory_confirm(
        message: Message,
        state: FSMContext,
):
    state_data = await state.get_data()
    category_id = state_data['category_id']
    subcategory_id = state_data['subcategory_id']
    if message.text.lower() == 'yes':
        with db_api.create_session() as session:
            subcategory = queries.get_subcategory(session, subcategory_id)
            if subcategory:
                queries.delete_subcategory(session, subcategory_id)
                session.commit()

                await message.reply(
                    '⌛️ Deleting Subcategory, Products and all of their images'
                    ' from the database and file system...\n'
                    'It will be refreshed in 5 seconds...'
                )
                await asyncio.sleep(
                    5)  # Add a delay of 5 seconds so the deletion finishes
                await message.answer(
                    '✅ Successfully Removed the Selected Subcategory!')

                category = queries.get_category(session, category_id)
                if category:
                    category_name = category.name
                    subcategories = queries.get_subcategories(
                        session=session,
                        category_id=category_id,
                    )
                    await CategoryMenuResponse(
                        update=message,
                        category_id=category_id,
                        category_name=category_name,
                        subcategories=subcategories,
                    )
                    await state.finish()
                else:
                    await message.reply(
                        f'⚠️ No category found with ID {category_id}.')
            else:
                await message.reply(
                    f'⚠️ No subcategory found with ID {subcategory_id}.')
    elif message.text.lower() == 'cancel':
        await state.finish()
        with db_api.create_session() as session:
            await CategoryMenuResponse(
                message, category_id,
                queries.get_category(session, category_id).name,
                queries.get_subcategories(session, category_id)
            )
    else:
        await message.reply(
            f'⚠️ You have to type either yes or cancel,'
            f' or otherwise use the menu to back to the category.'
        )
