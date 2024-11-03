from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from database import get_db_session
from translations import get_translation
from middlewares.access_middleware import access_required
from constants import *
from states import *

from models.user import User
from models.word import Word
from models.word_block import WordBlock

@access_required
async def add_block(update: Update, context: CallbackContext) -> int:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session=session)
        language_code = user.get_language_code()

        await update.message.reply_text(get_translation(language_code, 'word_block.add.rules'), parse_mode='MarkdownV2')

        return ADD_BLOCK_STATE

@access_required
async def add_block_callback(update: Update, context: CallbackContext) -> int:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session=session)
        language_code = user.get_language_code()

        errors = []
        words = []

        message_text = update.message.text.strip()

        if '\n' not in message_text:
            await update.message.reply_text(get_translation(language_code, 'word_block.add.error', errors='Title missing or incorrect format'))
            return ADD_BLOCK_STATE

        title, words_text = message_text.split('\n', 1)
        title = title.strip()

        if not title:
            errors.append('Title is empty')
        elif WordBlock.exists(title=title, user_id=user.id, session=session):
            await update.message.reply_text(get_translation(language_code, 'word_block.add.exists', title=title))
            return ADD_BLOCK_STATE

        for i, line in enumerate(words_text.splitlines()):
            line = line.strip()
            if '-' not in line:
                errors.append(f'Line {i + 1}: Missing '-' separator')
                continue

            word, translate = map(str.strip, line.split('-', 1))
            if not word or not translate:
                errors.append(f'Line {i + 1}: Missing word or translation')
            else:
                words.append((word, translate))

        if errors:
            await update.message.reply_text(
                get_translation(language_code, 'word_block.add.error', errors='\n'.join(errors))
            )
            return ADD_BLOCK_STATE

        word_block = WordBlock.create(title=title, user_id=user.id, session=session)
        session.flush()

        for word, translate in words:
            Word.create(word=word, translate=translate, word_block_id=word_block.id, session=session)

        await update.message.reply_text(get_translation(language_code, 'word_block.add.success', title=title))
        return ConversationHandler.END

@access_required
async def learn_block(update: Update, context: CallbackContext) -> int:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session=session)
        language_code = user.get_language_code()

        word_blocks = WordBlock.get_all_by_user_id(user_id=user.id, session=session)
        if not word_blocks:
            await update.message.reply_text(get_translation(language_code, 'word_block.learn.no_blocks'))
            return ConversationHandler.END

        await update.message.reply_text(
            get_translation(language_code, 'word_block.learn.select_block'),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(block.title, callback_data=f'{LEARN_BLOCK_CODE}{block.id}')]
                for block in word_blocks
            ])
        )

    return LEARN_BLOCK_STATE

@access_required
async def learn_block_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    telegram_user = update.effective_user

    block_id = query.data.split(LEARN_BLOCK_CODE)[1]

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session=session)
        language_code = user.get_language_code()

        word_block = WordBlock.get_by_id(block_id, session=session)
        words = Word.get_all_by_block_id(block_id=block_id, session=session)

        if words:
            word_list = '\n'.join([f'{word.word} - {word.translate}' for word in words])
            await query.edit_message_text(
                get_translation(language_code, 'word_block.learn.list_words', title=word_block.title, words=word_list)
            )
        else:
            await query.edit_message_text(
                get_translation(language_code, 'word_block.learn.no_words', title=word_block.title)
            )

    return ConversationHandler.END

@access_required
async def review_block(update: Update, context: CallbackContext) -> int:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session=session)
        language_code = user.get_language_code()

        word_blocks = WordBlock.get_all_by_user_id(user_id=user.id, session=session)
        if not word_blocks:
            await update.message.reply_text(get_translation(language_code, 'word_block.review.no_blocks'))
            return ConversationHandler.END

        await update.message.reply_text(
            get_translation(language_code, 'word_block.review.select_block'),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(block.title, callback_data=f'{REVIEW_BLOCK_CODE}{block.id}')]
                for block in word_blocks
            ])
        )

    return REVIEW_BLOCK_STATE

@access_required
async def review_block_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    telegram_user = update.effective_user

    block_id = query.data.split(REVIEW_BLOCK_CODE)[1]

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session=session)
        language_code = user.get_language_code()

        word_block = WordBlock.get_by_id(block_id, session=session)
        words = Word.get_all_by_block_id(block_id=block_id, session=session)

        if words:
            await query.edit_message_text(
                get_translation(language_code, 'word_block.review.list_words', title=word_block.title)
            )

            for word in words:
                await context.bot.send_message(chat_id=telegram_user.id, text=f'{word.translate} \- ||{word.word}||', parse_mode='MarkdownV2')
        else:
            await query.edit_message_text(
                get_translation(language_code, 'word_block.review.no_words', title=word_block.title)
            )

    return ConversationHandler.END

@access_required
async def delete_block(update: Update, context: CallbackContext) -> int:
    telegram_user = update.effective_user

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session=session)
        language_code = user.get_language_code()

        word_blocks = WordBlock.get_all_by_user_id(user_id=user.id, session=session)
        if not word_blocks:
            await update.message.reply_text(get_translation(language_code, 'word_block.delete.no_blocks'))
            return ConversationHandler.END

        await update.message.reply_text(
            get_translation(language_code, 'word_block.delete.select_block'),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(block.title, callback_data=f'{DELETE_BLOCK_CODE}{block.id}')]
                for block in word_blocks
            ])
        )

    return DELETE_BLOCK_STATE

@access_required
async def delete_block_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    telegram_user = update.effective_user

    block_id = query.data.split(DELETE_BLOCK_CODE)[1]

    with get_db_session() as session:
        user = User.get_by_telegram_id(telegram_user.id, session=session)
        language_code = user.get_language_code()

        word_block = WordBlock.get_by_id(_id=block_id, session=session)
        words = Word.get_all_by_block_id(block_id=word_block.id, session=session)
        if words:
            for word in words:
                Word.delete(_id=word.id, session=session)

        WordBlock.delete(_id=word_block.id, session=session)

        await query.edit_message_text(
            get_translation(language_code, 'word_block.delete.success', title=word_block.title)
        )

    return ConversationHandler.END
