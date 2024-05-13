from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from data import languages, messages


language_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton(v, callback_data=k)] for k, v in languages.items()]
)


async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    lang = query.data
    context.user_data['lang'] = lang
    await query.message.chat.send_message(messages['lang_set'][lang])
