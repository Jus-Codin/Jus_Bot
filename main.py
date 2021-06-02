from time import strftime, localtime, time
from Jus_Bot import Jus_Bot, open_web

import discord, os

print(strftime('%H:%M:%S', localtime(time())))

TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()

def get_prefix(bot, message: discord.Message):
  if message.content[:8].lower() == 'justest ':
    return message.content[:8]
  else:
    return discord.ext.commands.when_mentioned(bot, message)

bot = Jus_Bot(command_prefix=get_prefix, intents=intents, case_insensitive=True)

def get_extensions():
  _, __, file_names = next(os.walk('./Jus_Bot/Cogs/'))
  list_of_ext = []
  for name in file_names:
    name, ext = name.split('.')
    if ext == 'py':
      print(name)
      list_of_ext.append('Jus_Bot.Cogs.' + name)
  return list_of_ext

Extensions = get_extensions()

for extension in Extensions:
  bot.load_extension(extension)

open_web()
bot.run(TOKEN)