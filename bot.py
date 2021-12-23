from typing import Pattern
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ChatAction, InlineKeyboardMarkup, InlineKeyboardButton


import os
import uuid
import qrcode as qr

import pyshorteners as pyshort

TOKEN = os.environ['API_TOKEN_TESTBOT']

WAIT_FOR_TEXT = 0
WAIT_FOR_URL = 1


def start(update, context):
    update.message.reply_text(
        'Bienvenido :D\n')
    btnGit = InlineKeyboardButton(
        text='myGitHub',
        url='https://github.com/AmarelleDiArgento'
    )
    btnQr = InlineKeyboardButton(
        text='Generar QR',
        callback_data='qr'
    )
    btnShort = InlineKeyboardButton(
        text='Acortar Enlaces',
        callback_data='short'
    )

    update.message.reply_text(
        text='Estas son las opciones disponibles, selecciona una de ellas.',
        reply_markup=InlineKeyboardMarkup([
            [btnGit, btnQr],
            [btnShort]
        ])
    )


def qr_command_handler(update, context):
    update.message.reply_text('Que texto quieres convertir a QR?')
    return WAIT_FOR_TEXT


def qr_callback_handler(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text('Que texto quieres convertir a QR?')
    return WAIT_FOR_TEXT


def short_command_handler(update, context):
    update.message.reply_text('Que URL quieres acortar?')
    return WAIT_FOR_URL


def short_callback_handler(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text('Que URL quieres acortar?')
    return WAIT_FOR_URL


def input_reply_text(update):
    text = update.message.text
    user = update.message.chat

    update.message.reply_text('Repito a {}: {}'.format(user.first_name, text))


def genetate_qr(text):
    filename = '{}.jpg'.format(uuid.uuid1())
    img = qr.make(text)
    img.save(filename)
    return filename


def send_photo(filename, chat):
    chat.send_action(
        action=ChatAction.UPLOAD_PHOTO,
        timeout=None
    )
    chat.send_photo(
        photo=open(filename, 'rb')
    )
    os.unlink(filename)


def send_text(text, chat):
    chat.send_action(
        action=ChatAction.TYPING,
        timeout=None
    )
    chat.send_message(
        text=text
    )


def input_url(update, context):
    chat = update.message.chat
    url = update.message.text
    try:

        s = pyshort.Shortener()
        short = s.chilpit.short(url)
        # s.chilpit.expand('http://chilp.it/TEST')
        send_text(short, chat)
        return ConversationHandler.END
    except:
        send_text("Creo {}, que eso no es una URL valida.".format(
            chat.first_name), chat)


def input_text(update, context):
    # input_reply_text(update)

    chat = update.message.chat

    text = update.message.text

    filename = genetate_qr(text)
    send_photo(filename, chat)

    return ConversationHandler.END


if __name__ == '__main__':
    updater = Updater(
        token=TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler('start', start),
                CommandHandler('qr',  qr_command_handler),
                CommandHandler('short',  short_command_handler),
                CallbackQueryHandler(
                    pattern='qr',
                    callback=qr_callback_handler
                ),
                CallbackQueryHandler(
                    pattern='short',
                    callback=short_callback_handler
                )

            ],
            states={
                WAIT_FOR_TEXT: [
                    MessageHandler(Filters.text, input_text)
                ],
                WAIT_FOR_URL: [
                    MessageHandler(Filters.text, input_url)
                ]
            },
            fallbacks=[]
        ))

    updater.start_polling()
    print('Bot is running...')
    updater.idle()
