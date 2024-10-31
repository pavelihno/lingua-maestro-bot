from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from database import get_db_session
from translations import get_translation
from middlewares.access_middleware import admin_required
from constants import APPROVE_ACCESS_CODE, REJECT_ACCESS_CODE

from models.user import User
from models.access_request import AccessRequest

async def request_access(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session)

        # If the user doesn't exist in the database, create a new user
        if not user:
            user = User.create(session, telegram_id=telegram_user.id, username=telegram_user.username, is_active=False)

        language_code = user.get_language_code()
        access_request = AccessRequest.get_active_user_request(user.id, session)

        if access_request:
            await query.edit_message_text(text=get_translation(language_code, 'access.request_waiting'))
        else:
            new_access_request = AccessRequest.create(
                session=session,
                is_approved=False,
                is_active=True,
                user_id=user.id
            )

            await query.edit_message_text(text=get_translation(language_code, 'access.request_submitted'))

async def cancel_request_access(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session)

        if user:
            language_code = user.get_language_code()

            access_request = AccessRequest.get_active_user_request(user.id, session)

            if access_request:
                AccessRequest.update(
                    access_request.id,
                    session=session,
                    is_active=False
                )
                await query.edit_message_text(text=get_translation(language_code, 'access.request_canceled'))
            else:
                await query.edit_message_text(text=get_translation(language_code, 'access.request_not_found'))

@admin_required
async def approve_access(update: Update, context: CallbackContext) -> None:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session)
        language_code = user.get_language_code()

        active_requests = AccessRequest.get_active_requests(session)

        if not active_requests:
            await update.message.reply_text(get_translation(language_code, 'access.no_active_request'))
            return
        
        buttons = []
        for request in active_requests:
            buttons.append([
                InlineKeyboardButton(get_translation(language_code, 'buttons.approve_access', username=request.user.username), callback_data=f"{APPROVE_ACCESS_CODE}{request.id}"),
                InlineKeyboardButton(get_translation(language_code, 'buttons.reject_access', username=request.user.username), callback_data=f"{REJECT_ACCESS_CODE}{request.id}")
            ])

        await update.message.reply_text(
            get_translation(language_code, 'access.active_request'),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@admin_required
async def handle_access_request(update: Update, context: CallbackContext, is_approved: bool) -> None:
    query = update.callback_query
    telegram_user = update.effective_user
    request_user_id = int(query.data.split(APPROVE_ACCESS_CODE if is_approved else REJECT_ACCESS_CODE)[1])

    with get_db_session() as session:
        admin_user = User.get_by_telegram_id(telegram_user.id, session)
        language_code = admin_user.get_language_code()

        request_user = User.get_by_id(request_user_id ,session)
        access_request = AccessRequest.get_active_user_request(request_user.id, session)

        if access_request:
            AccessRequest.update(
                access_request.id,
                session=session,
                is_active=False,
                is_approved=is_approved
            )

            if is_approved:
                await query.edit_message_text(text=get_translation(language_code, 'access.request_approved', username=request_user.username))
            else:
                await query.edit_message_text(text=get_translation(language_code, 'access.request_rejected', username=request_user.username))
        else:
            await query.edit_message_text(text=get_translation(language_code, 'access.request_not_found'))

async def approve_access_callback(update: Update, context: CallbackContext) -> None:
    await handle_access_request(update, context, is_approved=True)

async def reject_access_callback(update: Update, context: CallbackContext) -> None:
    await handle_access_request(update, context, is_approved=False)
