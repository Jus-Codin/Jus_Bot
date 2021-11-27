from discord.ext import commands
from discord.commands import slash_command, message_command, user_command
from ..Utils import embed_template
from ..CodeRunner import run_code, format_code
import discord

class AppCommands(commands.Cog):
  
  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.hidden = True
    self.suppress = False

  @slash_command(name='ping', description='Get the websocket latency', guild_ids=[837579283991887892, 914057960827781130])
  async def ping(self, ctx):
    embed = embed_template(ctx, title='Pong! \U0001F3D3', description=f'{round(self.bot.latency*1000,1)}ms')
    await ctx.respond(embed=embed)

  @message_command(name='Run Code', guild_ids=[837579283991887892, 914057960827781130])
  async def runcode(self, ctx, message: discord.Message):
    lang, code = format_code(message.content)

    if not lang:
      return await ctx.respond('The code must be in a code block', ephemeral=True)
      
    s = await run_code(code, message.author.mention, lang)

    await ctx.respond(s)

  @user_command(name='User Info', guild_ids=[837579283991887892, 914057960827781130])
  async def user_info(self, ctx, member: discord.Member):
    colour = member.accent_colour if member.accent_colour else member.colour
    avatar = member.display_avatar.url

    name = str(member)
    nickname = member.nick

    created = discord.utils.format_dt(member.created_at)
    joined = discord.utils.format_dt(member.joined_at)

    guild_perms = [p[0] for p in member.guild_permissions if p[1]]
    channel_perms = [p[0] for p in ctx.channel.permissions_for(member) if p[1]]

    roles = [r.mention for r in member.roles[1:]] if member.roles[1:] else ['None']
    top_role = member.top_role.mention

    embed = embed_template(ctx, colour=colour, title=name)
    embed.set_thumbnail(url=avatar)
    embed.add_field(name='Nickname', value=nickname)
    embed.add_field(name='Account Created on', value=created)
    embed.add_field(name='Joined server on', value=joined)
    embed.add_field(name='Roles', value='\n'.join(roles))
    embed.add_field(name='Top Role', value=top_role)
    embed.add_field(name='Server Perms', value='```\n{}```'.format('\n'.join(guild_perms)), inline=False)
    embed.add_field(name='Channel Perms', value='```\n{}```'.format('\n'.join(channel_perms)))

    await ctx.respond(embed=embed)

def setup(bot):
  bot.add_cog(AppCommands(bot))