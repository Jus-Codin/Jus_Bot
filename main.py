from Jus_Bot import JusBot, get_setup_from_env

import logging

from web import open_web

setup = get_setup_from_env()

logging.basicConfig(level=logging.INFO)

bot = JusBot(setup)

open_web()
bot.run()