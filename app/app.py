import os

from telegram import Update
from telegram.ext import Application, CommandHandler

from database import init_db
from translations import configure_i18n

from handlers.user_handler import start

TELEGRAM_BOT_SECRET_KEY = os.environ.get('TELEGRAM_BOT_SECRET_KEY')
TELEGRAM_BOT_TIMEOUT = int(os.environ.get('TELEGRAM_BOT_TIMEOUT'))

def main():

    configure_i18n()

    print('Connecting to DB')
    init_db()
    print('Connected to DB')

    application = Application.builder().token(TELEGRAM_BOT_SECRET_KEY).build()

    # add handlers
    application.add_handler(CommandHandler('start', start))

    application.run_polling(timeout=TELEGRAM_BOT_TIMEOUT)


if __name__ == '__main__':
    main()