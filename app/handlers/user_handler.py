from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from database import get_db_session
from translations import get_translation
from middlewares.access_middleware import access_required
from constants import CHANGE_LANGUAGE_CODE

from models.user import User
from models.language import Language

@access_required
async def start(update: Update, context: CallbackContext) -> None:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session)

        language_code = user.get_language_code() if user else User.get_default_language_code()

        reply_message = get_translation(language_code, 'user.start')

        await update.message.reply_text(reply_message)

async def cancel(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    print(query)

    await query.edit_message_reply_markup(reply_markup=None)


@access_required
async def change_language(update: Update, context: CallbackContext) -> None:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session)
        language_code = user.get_language_code()

        languages = Language.get_all(session)

        keyboard = [
            [InlineKeyboardButton(language.name, callback_data=f'{CHANGE_LANGUAGE_CODE}{language.code}') for language in languages]
        ]

        reply_message = get_translation(language_code, 'user.select_language')
        await update.message.reply_text(reply_message, reply_markup=InlineKeyboardMarkup(keyboard))

@access_required
async def change_language_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session)
        current_language_code = user.get_language_code() 

        selected_language_code = query.data.split(CHANGE_LANGUAGE_CODE)[1]
        selected_language = Language.get_by_code(selected_language_code, session)

        if selected_language:
            User.update(user.id, session, language_id=selected_language.id)

            reply_message = get_translation(selected_language_code, 'user.language_changed', language_name=selected_language.name)

            await query.edit_message_text(text=reply_message)
        else:
            await query.answer(get_translation(current_language_code, 'user.language_not_found'))
