import telebot
import telegram
from decouple.config import TOKEN
import decouple.functions as func
bot = telebot.TeleBot(TOKEN)
state = func.INIT


import telegram
import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
# initialiate update_id
update_id = None

def main():
    global update_id
    ## create bot
    bot = telegram.Bot(TOKEN)

    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None
    # track log
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # main function
    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:

            update_id += 1
#
def echo(bot):
    global update_id
    # refresh after the last update_id
    global state
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # if BOT receive the message

            state,response = func.send_message(state,message=update.message.text)
            # response is what the information that robot want
            # to answer
            print(response)
            update.message.reply_text(response)
# run MAIN function here
if __name__ == '__main__':
    main()

