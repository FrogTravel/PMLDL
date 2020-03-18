
token = "1138687907:AAHn8gss3caT_ihrjogeICCXATcx6FquhLU"
"""
Basic example for a bot that uses inline keyboards.
"""
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import joke_generator

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

joke_id = 0

def joke(update, context):
    keyboard = [[InlineKeyboardButton("👍", callback_data='1'),
                 InlineKeyboardButton("👎", callback_data='2')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    joke = joke_generator.generate_joke()
    # joke_id = from joke generator don't generate a string but a Joke as an object with id

    update.message.reply_text(joke, reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query
    data = query.data
    if data == '1':
        joke_generator.positive_grade(joke_id)
    elif data == '2':
        joke_generator.negative_grade(joke_id)

    query.edit_message_text(text="Thank you for your feedback")



def start(update, context):
    update.message.reply_text("Use /joke to generate a joke")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('joke', joke))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()