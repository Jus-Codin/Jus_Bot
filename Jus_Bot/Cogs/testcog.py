import discord
from discord.ext import commands
from ..Utils.paginator import Paginator
from ..Utils.ui import PaginatorView

class Test(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.hidden = False

  @commands.command()
  async def testView(self, ctx):

    class View(discord.ui.View):
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)

      @discord.ui.select(custom_id="Some identifier", placeholder="Placeholder", min_values=1, max_values=1, options=[discord.SelectOption(label="Hello", emoji="😳")])
      async def callback(self, select: discord.ui.select, interaction: discord.Interaction):
          await interaction.response.send_message('Hello', ephemeral=True) # to get the select options, you can use interaction.data

    await ctx.send('Test', view=View())

  @commands.command()
  async def paginView(self, ctx):
    paginator = Paginator([{'content':'test1'}, {'content':'test2'}, {'embeds':[discord.Embed(title='Test', description='This is a test')]}])
    view = PaginatorView(paginator)
    await view.send_to(ctx)

def setup(bot):
  bot.add_cog(Test(bot))