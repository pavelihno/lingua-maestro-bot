import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from database import init_db
from translations import configure_i18n
from constants import CHANGE_LANGUAGE_CODE, REQUEST_ACCESS_CODE, CANCEL_REQUEST_ACCESS_CODE, \
    APPROVE_ACCESS_CODE, REJECT_ACCESS_CODE

from handlers.user_handler import start, cancel, change_language, change_language_callback
from handlers.access_handler import request_access, cancel_request_access, approve_access, \
    approve_access_callback, reject_access_callback

TELEGRAM_BOT_SECRET_KEY = os.environ.get('TELEGRAM_BOT_SECRET_KEY')
TELEGRAM_BOT_TIMEOUT = int(os.environ.get('TELEGRAM_BOT_TIMEOUT'))

def main():

    configure_i18n()

    print('Connecting to DB')
    init_db()
    print('Connected to DB')

    application = Application.builder().token(TELEGRAM_BOT_SECRET_KEY).build()

    application.add_handlers({
        0: [
            CommandHandler('start', start),
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CommandHandler('change_language', change_language),
            CallbackQueryHandler(change_language_callback, pattern=rf'^{CHANGE_LANGUAGE_CODE}[a-z]+$'),

            CallbackQueryHandler(request_access, pattern=rf'^{REQUEST_ACCESS_CODE}$'),
            CallbackQueryHandler(cancel_request_access, pattern=f'^{CANCEL_REQUEST_ACCESS_CODE}$'),
            CommandHandler('approve_access', approve_access),
            CallbackQueryHandler(approve_access_callback, pattern=rf'^{APPROVE_ACCESS_CODE}\d+$'),
            CallbackQueryHandler(reject_access_callback, pattern=rf'^{REJECT_ACCESS_CODE}\d+$'),
        ]
    })


    application.run_polling(timeout=TELEGRAM_BOT_TIMEOUT)


if __name__ == '__main__':
    main()