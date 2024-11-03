from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from database import get_db_session
from translations import get_translation
from middlewares.access_middleware import access_required
from constants import *
from states import *

from models.user import User
from models.language import Language

@access_required
async def start(update: Update, context: CallbackContext) -> int:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session)

        language_code = user.get_language_code() if user else User.get_default_language_code()

        await update.message.reply_text(get_translation(language_code, 'user.start'))

    return START_STATE

async def help(update: Update, context: CallbackContext) -> int:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session)

        language_code = user.get_language_code() if user else User.get_default_language_code()

        await update.message.reply_text(get_translation(language_code, 'user.help'))

    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    query = update.callback_query

    await query.edit_message_reply_markup(reply_markup=None)

    return ConversationHandler.END

@access_required
async def change_language(update: Update, context: CallbackContext) -> int:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session)
        language_code = user.get_language_code()

        languages = Language.get_all(session)

        await update.message.reply_text(get_translation(language_code, 'user.select_language'), reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(language.name, callback_data=f'{CHANGE_LANGUAGE_CODE}{language.code}')
                for language in languages
            ]
        ]))

    return CHANGE_LANGUAGE_STATE

@access_required
async def change_language_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session)
        current_language_code = user.get_language_code() 

        selected_language_code = query.data.split(CHANGE_LANGUAGE_CODE)[1]
        selected_language = Language.get_by_code(selected_language_code, session)

        if selected_language:
            User.update(user.id, session=session, language_id=selected_language.id)
            await query.edit_message_text(text=get_translation(selected_language_code, 'user.language_changed', language_name=selected_language.name))
        else:
            await query.answer(get_translation(current_language_code, 'user.language_not_found'))

    return ConversationHandler.END
