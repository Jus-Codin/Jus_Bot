from discord.ext import commands
from difflib import get_close_matches
from .templates import embed_template, error_template
import discord
import traceback

async def error_handler(ctx: commands.Context, error, suppress=False):
  try:
    if isinstance(error, commands.MissingRequiredArgument):
      if not ctx.command.hidden and not ctx.cog.hidden:
        embed = embed_template(ctx)
        embed.title, embed.description = ctx.command.name, ctx.command.help

        if len(ctx.command.aliases):
          aliases = '\n'.join(ctx.command.aliases)
        else:
          aliases = 'None'
        embed.add_field(name='Aliases', value=f'```\n{aliases}```', inline=False)

        preview = f'```Jus {ctx.command.name} {ctx.command.signature}```'
        embed.add_field(name='Usage', value=preview)

        await ctx.send(embed=embed)
    else:
      if isinstance(error, commands.errors.CommandNotFound):
        embed = error_template(ctx, type='NotFound')
        message = '```cOmMaNd DoEsN\'t ExIsT```'
        command = ctx.message.content.split()[1]
        matches = get_close_matches(command, list(map(lambda c: c.name, filter(lambda c: not c.hidden and not c.cog.hidden, ctx.bot.walk_commands()))))
        if matches:
          embed.add_field(name='Did you mean:', value=f'```{chr(10).join(matches)}```')
      elif isinstance(error, commands.MissingPermissions):
        embed = error_template(ctx, type='BadPerms')
        message = '```Your permissions are far inferior for this command```'
      elif isinstance(error, commands.errors.NotOwner):
        embed = error_template(ctx, type='BadPerms')
        message = '```Only the owner of the bot can run this command```'
      elif isinstance(error, commands.errors.NoPrivateMessage):
        embed = error_template(ctx)
        message = '```This command can only be run in Servers!```'
      else:
        embed = error_template(ctx)
        trace_string = '\n'.join(traceback.format_exception(type(error), error,   error.__traceback__))
        if suppress:
          print(trace_string)
          message = '```Command raised an exception, but error suppression is enabled```'
        elif len(trace_string) <= 4089:
          message = f'```\n{trace_string}```'
        else:
          message = '```Traceback too large to send, printed in console instead```'
          print(trace_string)
      
      embed.description = message
      await ctx.send(embed=embed)
  except discord.errors.Forbidden:
    pass