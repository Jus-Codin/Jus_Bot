from discord.ext import commands

class CogManager(commands.Cog):
  """> Commands to manage bot cogs"""

  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.hidden = True

  @commands.command()
  @commands.is_owner()
  async def reload_cog(self, ctx, cog_name):
    name = 'Jus_Bot.Cogs.' + cog_name
    self.bot.reload_extension(name)
    await ctx.send('Extension successfully reloaded')
  
  @commands.command()
  @commands.is_owner()
  async def load_cog(self, ctx, cog_name):
    name = 'Jus_Bot.Cogs.' + cog_name
    self.bot.load_extension(name)

  @commands.command()
  @commands.is_owner()
  async def unload_cog(self, ctx, cog_name):
    name = 'Jus_Bot.Cogs.' + cog_name
    self.bot.unload_extension(name)  

  @commands.command()
  @commands.is_owner()
  async def add_cog(self, ctx, cog_name):
    name = 'Jus_Bot.Cogs.' + cog_name + '.py'
    self.bot.load_extension(name)

def setup(bot):
  bot.add_cog(CogManager(bot))