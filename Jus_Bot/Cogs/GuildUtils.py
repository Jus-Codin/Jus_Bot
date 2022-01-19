import discord
from discord.ext import commands
from ..Utils import embed_template

class GuildUtils(commands.Cog):
  """> Contains commands that can be used in servers"""

  def __init__(self, bot):
   self.bot: commands.Bot = bot
   self.hidden = False
   self.suppress = False

  @commands.command(help='> Sends info about the server you are in')
  @commands.guild_only()
  async def server(self, ctx):
    guild: discord.Guild = ctx.guild
    prefix = '> '

    name = guild.name
    desc = prefix + guild.description if guild.description else discord.Embed.Empty
    icon = guild.icon.url
    created = prefix + discord.utils.format_dt(guild.created_at)

    owner = prefix + str(guild.owner)

    guild_id = prefix + str(guild.id)

    verify_lvl = prefix + str(guild.verification_level).capitalize()

    nitro_tier = prefix + str(guild.premium_tier)
    boosts = prefix + str(guild.premium_subscription_count)
    boosters = prefix + str(len(guild.premium_subscribers))

    channels = prefix + str(len(guild.channels))
    threads = prefix + str(len(guild.threads))
    active_threads = prefix + str(len(await guild.active_threads()))
    voice_channels = prefix + str(len(guild.voice_channels))
    stages = prefix + str(len(guild.stage_channels))
    text_channels = prefix + str(len(guild.text_channels))

    roles = prefix + str(len(guild.roles))

    members = prefix + str(guild.member_count)

    embed = embed_template(ctx, title=name, description=desc
    ).set_thumbnail(url=icon
    ).add_field(name='Server Owner', value=owner
    ).add_field(name='Created on', value=created, inline=False
    ).add_field(name='Guild ID', value=guild_id
    ).add_field(name='Total Channels', value=channels
    ).add_field(name='Roles', value=roles
    ).add_field(name='Total Members', value=members
    ).add_field(name='Verification Level', value=verify_lvl
    ).add_field(name='Server Nitro Tier', value=nitro_tier
    ).add_field(name='Boosts', value=boosts
    ).add_field(name='Boosters', value=boosters
    ).add_field(name='Text Channels', value=text_channels
    ).add_field(name='Threads', value=threads
    ).add_field(name='Active Threads', value=active_threads
    ).add_field(name='Stages', value=stages
    ).add_field(name='Voice Channels', value=voice_channels)

    await ctx.reply(embed=embed)

  @commands.command(
    help='> Find info about someone in this server',
    aliases=[
      'whois',
      'getmember',
      'userinfo',
      'getuser'
    ]
  )
  @commands.guild_only()
  async def memberinfo(self, ctx, member: discord.Member):
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

    await ctx.reply(embed=embed)



def setup(bot):
  bot.add_cog(GuildUtils(bot))