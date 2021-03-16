from time import strftime, localtime, time
from Jus_Bot import Jus_Bot

import discord, os

print(strftime('%H:%M:%S', localtime(time())))
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.members = True

def get_prefix(bot, message: discord.Message):
  if message.content[:8].lower() == 'justest ':
    return message.content[:8]
  else:
    return 'JusTest '

bot = Jus_Bot(command_prefix=get_prefix, intents=intents, case_insensitive=True)

Extensions = [
  'Jus_Bot.Cogs.Dianogstics'
]

for extension in Extensions:
  bot.load_extension(extension)

bot.run(TOKEN)