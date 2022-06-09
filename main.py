from Jus_Bot import JusBot, get_setup_from_env

setup = get_setup_from_env()

bot = JusBot(setup)

bot.run()