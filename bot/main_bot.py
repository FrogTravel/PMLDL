from joke_generator import JokeGenerator
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import logging

"""
Basic example for a bot that uses inline keyboards.
"""
# TODO: Move to config
token = "1180357649:AAF94C2hSNlPsM13_Ie1kGg_FvJvbMRYuwk"


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: move to config file (model_path, max_len, buffer size, cuda/cpu)
joke_generator = JokeGenerator(model_path='model')

splitter = "::"
pos = "1"
neg = "2"


def joke_command_handler(update, context):
    # update.send_chat_action(chat_id=context, action=telegram.ChatAction.TYPING)
    # update.message.reply_text("Generating a joke")  # This message not disappears
    general_joke_handler(update, context, promt_text="")


def text_handler(update, context):
    question = update.message.text
    general_joke_handler(update, context, question)


def general_joke_handler(update, context, promt_text=""):
    joke = joke_generator.generate_joke(promt=promt_text)
    joke_id = joke.id

    keyboard = [[InlineKeyboardButton("👍", callback_data=f'{joke_id}{splitter}{pos}'),
                 InlineKeyboardButton("👎", callback_data=f'{joke_id}{splitter}{neg}')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        joke.text, reply_markup=reply_markup, parse_mode=telegram.ParseMode.HTML)


def button_handler(update, context):
    query = update.callback_query
    data = query.data
    (joke_id, rating) = data.rsplit(splitter, 1)
    user_id = query.message.chat.id
    if rating == pos:
        joke_generator.positive_grade(user_id=user_id, joke_id=joke_id)
    elif rating == neg:
        joke_generator.negative_grade(user_id=user_id, joke_id=joke_id)
    query.message.reply_text("Thank you for your feedback")


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

    updater.dispatcher.add_handler(
        CommandHandler('joke', joke_command_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_handler))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(text_handler))
    updater.dispatcher.add_error_handler(error)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, text_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
