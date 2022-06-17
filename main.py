from Jus_Bot import JusBot, get_setup_from_env

import logging

setup = get_setup_from_env()

logging.basicConfig(level=logging.INFO)

bot = JusBot(setup)

bot.run()