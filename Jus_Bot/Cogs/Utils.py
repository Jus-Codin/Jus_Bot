import discord
from discord.ext import commands
from ..Utils.paginator import Paginator, PaginatorInterface

class Utils(commands.Cog):
  """Contains commands for more info on commands"""

  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.hidden = False

  @commands.command()
  async def help(self, ctx, *args):
    embeds = []
    main_embed = discord.Embed(title='List of Command Catergories')
    main_embed.set_author(name="Jus_Bot", icon_url=self.bot.user.display_avatar.url)
    cog_found = False
    found = False
    footer = 'Use `Jusdev help [Catergory]/[Command]` to find out more about them!\n(Is case-sensitive)'

    for i in self.bot.cogs:
      if not self.bot.cogs[i].hidden:
        if not args:
          main_embed.add_field(name=i, value=self.bot.cogs[i].__doc__, inline=True)
          main_embed.set_footer(text=footer)

        embed = discord.Embed()
        embed.set_author(name="Jus_Bot", icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=footer)

        if not args or i == args:
          cog_found = (i == args)
          embed.title, embed.description = f'{i} Command Listing', self.bot.cogs[i].__doc__

        for command in self.bot.cogs.get(i).walk_commands():
          if not command.hidden:
            if cog_found or not args:
              embed.add_field(name=command.name, value=command.help, inline=True)
            elif command.name == args[0]:
              found = True
              embed.title, embed.description = command.name, command.help

        embeds.append({'embeds':[embed]})

        if found:
          break

    if not args:
      embeds.insert(0, {'embeds':[main_embed]})
  
    elif not found and not cog_found:
      embed = discord.Embed()
      embed.set_author(name="Jus_Bot", icon_url=self.bot.user.display_avatar.url)
      embed.set_footer(text=footer)
      embed.title, embed.description, embed.colour = 'Error!', f'How do you even use "{args}"?', discord.Color.red()

      embeds = [{'embeds':[embed]}]

    paginator = Paginator(embeds)
    await PaginatorInterface(self.bot, paginator).send_to(ctx)

def setup(bot):
  bot.add_cog(Utils(bot)) 