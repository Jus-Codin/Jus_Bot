import discord
from discord.ext import commands
from ..Utils import Paginator, PaginatorView

class Utils(commands.Cog):
  """> Contains commands for more info on commands"""

  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.hidden = False

  @commands.command(help='> Gives you help for a command or catergory')
  async def help(self, ctx, arg=None):
    embeds = []
    main_embed = discord.Embed(title='List of Command Catergories')
    main_embed.set_author(name="Jus_Bot", icon_url=self.bot.user.display_avatar.url)
    cog_found = None
    found = False
    footer = 'Use `Jusdev help [Catergory]/[Command]` to find out more about them!\n(Is case-sensitive)'

    for i in self.bot.cogs:
      if not self.bot.cogs[i].hidden:
        if not arg:
          main_embed.add_field(name=i, value=self.bot.cogs[i].__doc__, inline=True)
          main_embed.set_footer(text=footer)

        embed = discord.Embed()
        embed.set_author(name="Jus_Bot", icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=footer)

        if not arg:
          embed.title, embed.description = f'{i} Command Listing', self.bot.cogs[i].__doc__

        elif i.lower() == arg.lower():
          cog_found = i if (i.lower() == arg.lower()) else None
          embed.title, embed.description = f'{i} Command Listing', self.bot.cogs[i].__doc__

        for command in self.bot.cogs.get(i).walk_commands():
          if not command.hidden:
            if cog_found == i or not arg:
              embed.add_field(name=command.name, value=command.help, inline=True)
            elif command.name.lower() == arg.lower():
              found = True
              embed.title, embed.description = command.name, command.help

        if any((not arg, cog_found == i, found)):
          embeds.append({'embeds':[embed]})

        if found:
          break

    if not arg:
      embeds.insert(0, {'embeds':[main_embed]})
  
    elif not found and not cog_found:
      embed = discord.Embed()
      embed.set_author(name="Jus_Bot", icon_url=self.bot.user.display_avatar.url)
      embed.set_footer(text=footer)
      embed.title, embed.description, embed.colour = '> Error!', f'How do you even use "{arg}"?', discord.Color.red()

      embeds = [{'embeds':[embed]}]

    paginator = Paginator(embeds)
    await PaginatorView(paginator).send_to(ctx)

def setup(bot):
  bot.add_cog(Utils(bot)) 