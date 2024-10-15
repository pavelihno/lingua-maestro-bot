import os

from telegram import Update
from telegram.ext import Application, CommandHandler

from database import init_db

from handlers.welcome_handler import start

TELEGRAM_BOT_SECRET_KEY = os.environ.get('TELEGRAM_BOT_SECRET_KEY')
TELEGRAM_BOT_TIMEOUT = int(os.environ.get('TELEGRAM_BOT_TIMEOUT'))

def main():

    print('Connecting to DB')

    init_db()

    print('Connected to DB')

    print('Launching bot')

    application = Application.builder().token(TELEGRAM_BOT_SECRET_KEY).build()

    # add handlers

    print('Adding handlers')
    application.add_handler(CommandHandler('start', start))

    print('Handlers added')

    application.run_polling(timeout=TELEGRAM_BOT_TIMEOUT)

    print('Bot launched')


if __name__ == '__main__':
    main()