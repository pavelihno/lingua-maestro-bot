import os

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters

from database import init_db
from translations import configure_i18n
from constants import *
from states import *

from handlers.user_handler import start, cancel, change_language, change_language_callback
from handlers.access_handler import request_access, cancel_request_access, approve_access, \
    approve_access_callback, reject_access_callback
from handlers.word_block_controller import add_block, add_block_callback, learn_block, \
    learn_block_callback, review_block, review_block_callback, delete_block, delete_block_callback

FUNCTION_URL = os.environ.get('FUNCTION_URL')
TELEGRAM_BOT_SECRET_KEY = os.environ.get('TELEGRAM_BOT_SECRET_KEY')
TELEGRAM_BOT_TIMEOUT = int(os.environ.get('TELEGRAM_BOT_TIMEOUT'))

def main():

    filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

    configure_i18n()

    print('Connecting to DB')
    init_db()
    print('Connected to DB')

    application = Application.builder().token(TELEGRAM_BOT_SECRET_KEY).build()

    application.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('change_language', change_language),
            CommandHandler('approve_access', approve_access),
            CommandHandler('add_block', add_block),
            CommandHandler('learn_block', learn_block),
            CommandHandler('review_block', review_block),
            CommandHandler('delete_block', delete_block),
        ],
        states={
            CHANGE_LANGUAGE_STATE: [
                CallbackQueryHandler(change_language_callback, pattern=rf'^{CHANGE_LANGUAGE_CODE}[a-z]+$'),
            ],
            REQUEST_ACCESS_STATE: [
                CallbackQueryHandler(request_access, pattern=rf'^{REQUEST_ACCESS_CODE}$'),
                CallbackQueryHandler(cancel_request_access, pattern=f'^{CANCEL_REQUEST_ACCESS_CODE}$'),
                CallbackQueryHandler(approve_access_callback, pattern=rf'^{APPROVE_ACCESS_CODE}\d+$'),
                CallbackQueryHandler(reject_access_callback, pattern=rf'^{REJECT_ACCESS_CODE}\d+$'),
            ],
            ADD_BLOCK_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_block_callback)
            ],
            LEARN_BLOCK_STATE: [
                CallbackQueryHandler(learn_block_callback, pattern=rf'^{LEARN_BLOCK_CODE}\d+$')
            ],
            REVIEW_BLOCK_STATE: [
                CallbackQueryHandler(review_block_callback, pattern=rf'^{REVIEW_BLOCK_CODE}\d+$')
            ],
            DELETE_BLOCK_STATE: [
                CallbackQueryHandler(delete_block_callback, pattern=rf'^{DELETE_BLOCK_CODE}\d+$')
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel, pattern='^cancel$'),
        ],
        allow_reentry=True
    ))

    application.run_polling(timeout=TELEGRAM_BOT_TIMEOUT)

    # application.run_webhook(
    #     listen="0.0.0.0",
    #     port=8443,
    #     webhook_url=FUNCTION_URL
    # )

if __name__ == '__main__':
    main()