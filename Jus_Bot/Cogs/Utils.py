import discord
from discord.commands import SlashCommand
from discord.ext import commands, tasks
from ..Utils import Paginator, PaginatorView, embed_template

class Utils(commands.Cog):
  """> Contains helpful commands"""

  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.hidden = False
    self.suppress = False
    self.update_presence.start()

  def cog_unload(self):
    self.update_presence.cancel()

  @tasks.loop(minutes=5)
  async def update_presence(self):
    activity = discord.Game(name='with the API | Jusdev help')
    await self.bot.change_presence(activity=activity)

  @update_presence.before_loop
  async def checker(self):
    await self.bot.wait_until_ready()

  @commands.command(help='> Gives you help for a command or catergory')
  async def help(self, ctx, arg=None):
    embeds = []
    main_embed = embed_template(ctx, title='List of Command Catergories')
    cog_found = None
    found = False
    extra = 'Use `Jusdev help [Catergory]/[Command]` to find out more!\n(Is case-sensitive)'

    for i in self.bot.cogs:
      if not self.bot.cogs[i].hidden:
        if not arg:
          main_embed.add_field(name=i, value=self.bot.cogs[i].__doc__, inline=True)

        embed = embed_template(ctx)

        if not arg:
          embed.title, embed.description = f'{i} Command Listing', self.bot.cogs[i].__doc__

        elif i.lower() == arg.lower():
          cog_found = i if (i.lower() == arg.lower()) else None
          embed.title, embed.description = f'{i} Command Listing', self.bot.cogs[i].__doc__

        for command in self.bot.cogs.get(i).walk_commands():
          if not isinstance(command, SlashCommand) and not command.hidden:
            if cog_found == i or not arg:
              embed.add_field(name=command.name, value=command.help, inline=True)
            elif command.name.lower() == arg.lower():
              found = True
              embed.title, embed.description = command.name, command.help

              if len(command.aliases):
                aliases = '\n'.join(command.aliases)
              else:
                aliases = 'None'
              embed.add_field(name='Aliases', value=f'```\n{aliases}```', inline=False)

              preview = f'```Jusdev {command.name} {command.signature}```'
              embed.add_field(name='Usage', value=preview)

        if any((not arg, cog_found == i, found)):
          embed.add_field(name='\u200b', value=extra, inline=False)
          embeds.append({'embeds':[embed]})

        if found:
          break

    if not arg:
      main_embed.add_field(name='\u200b', value=extra, inline=False)
      embeds.insert(0, {'embeds':[main_embed]})
  
    elif not found and not cog_found:
      embed = embed_template(ctx)
      embed.add_field(name='\u200b', value=extra, inline=False)
      embed.title, embed.description, embed.colour = 'Error!', f'> How do you even use "{arg}"?', discord.Color.red()

      embeds = [{'embeds':[embed]}]

    paginator = Paginator(embeds)
    await PaginatorView(paginator).send_to(ctx)

def setup(bot):
  bot.add_cog(Utils(bot)) 