import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters

from data import messages
from keyboards import language_keyboard, language_handler


load_dotenv(find_dotenv())
TOKEN = os.getenv('TELEGRAM_TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Выберете язык общения с ботом.', reply_markup=language_keyboard)


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(messages['on_text'][lang])


async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(messages['on_voice'][lang])


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    imgdir = Path('photos')
    imgdir.mkdir(exist_ok=True)
    image = await update.message.photo[-1].get_file()
    await image.download_to_drive(imgdir / Path(image.file_path).name)

    lang = context.user_data.get('lang', 'en')
    await update.message.reply_text(messages['on_photo'][lang])


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    print('Started ...')

    # commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_handler))

    # messages
    app.add_handler(MessageHandler(filters.TEXT, text))
    app.add_handler(MessageHandler(filters.VOICE, voice))
    app.add_handler(MessageHandler(filters.PHOTO, photo))

    app.run_polling()
    print('Stopped.')


if __name__ == "__main__":
    main()
