from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from database import get_db_session
from translations import get_translation
from models.user import User
from models.access_request import AccessRequest

from constants import REQUEST_ACCESS_CODE, CANCEL_REQUEST_ACCESS_CODE

def access_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs) -> None:
        telegram_user = update.effective_user

        with get_db_session() as session:
            user = User.get_by_telegram_id(telegram_user.id, session)

            if user and user.is_active:
                return await func(update, context, *args, **kwargs)

            language_code = user.get_language_code() if user else User.get_default_language_code()

            # Check if the user has an active access request
            access_request = AccessRequest.get_active_user_request(user.id, session) if user else None

            if not access_request:
                # no access request
                reply_message = get_translation(language_code, 'access.request_access')
                keyboard = [
                    [
                        InlineKeyboardButton(get_translation(language_code, 'buttons.request_access'), callback_data=REQUEST_ACCESS_CODE),
                        InlineKeyboardButton(get_translation(language_code, 'buttons.cancel'), callback_data='cancel')
                    ]
                ]

            else:
                # waiting for approval
                reply_message = get_translation(language_code, 'access.request_waiting')
                keyboard = [
                    [
                        InlineKeyboardButton(get_translation(language_code, 'buttons.cancel_request_access'), callback_data=CANCEL_REQUEST_ACCESS_CODE)
                    ]
                ]

        await update.message.reply_text(reply_message, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    return wrapper

def admin_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs) -> None:
        telegram_user = update.effective_user

        with get_db_session() as session:
            user = User.get_by_telegram_id(telegram_user.id, session)
            language_code = user.get_language_code()

            if not user or not user.is_superuser:
                reply_text = get_translation(language_code, 'access.no_permission')

                if update.message:
                    await update.message.reply_text(reply_text)
                elif update.callback_query:
                    await update.callback_query.answer(reply_text)

                return

        return await func(update, context, *args, **kwargs)

    return wrapper
