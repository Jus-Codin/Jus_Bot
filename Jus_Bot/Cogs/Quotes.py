from discord.ext import commands
from ..Utils import quotes

class Quotes(commands.Cog):
  """> Get quotes from various APIs"""

  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.hidden = False

  @commands.command(help='> Get the quote of the day')
  async def qod(self, ctx, category='inspire'):
    quote = await quotes.tss_qod(category)
    await ctx.send(quote)

  @commands.command(help='> Get a inspirational quote')
  async def inspquote(self, ctx):
    quote = await quotes.forismatic()
    await ctx.send(quote)
  
  @commands.command(help='> Get a random paper quote')
  async def paperquote(self, ctx, language='en'):
    quote = await quotes.paper(language)
    await ctx.send(quote)

def setup(bot):
  bot.add_cog(Quotes(bot))