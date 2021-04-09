import discord
from discord.ext import commands
from ..Utils import WolframClient, PaginatorInterface, Paginator
import os

class WebUtils(commands.Cog):
  """Commands to get info from the internet"""

  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.client = WolframClient(os.getenv('APPID'))

  @commands.command()
  async def wolfram(self, ctx, *args):

    embeds = []

    res = await self.client.query(' '.join(args))
    if res['@success'] == 'true':

      # Get assumption, if any
      assumptions = res.assumptions
      try:
        assumption = next(assumptions)['assumption']
        if isinstance(assumption, list):
          assumption = assumption[0]
        text = assumption.get('@template')
        text = text.replace('${desc1}', assumption['value'][0]['@desc'])
        try:
          if assumption['@word']:
            text = text.replace('${word}', assumption['@word'])
          else:
            text = text.replace('${word1}', assumption['value'][0]['@word'])
        except Exception:
          pass
        assumption = text[:text.index('. ')+1]
      except StopIteration:
        assumption = 'None'

      # Get warnings, if any
      warnings = []
      for warning in res.warnings:
        if warning == None:
          break
        warnings.append(list(warning.items())[1][1]['@text'])

      for pod in res.pods:
        if pod.text:
          embed = discord.Embed(title='Results from Wolfram|Alpha',
                                description='Powered by Wolfram|Alpha v2.0 API',
                                url='https://www.wolframalpha.com/',
                                colour=discord.Color.orange())
          embed.add_field(name='Assumption', value=assumption)
          if warnings:
            embed.add_field(name='Warnings', value='\n'.join(warnings))
          embeds.append(embed.add_field(name=pod.title, value=pod.text, inline=False))
    
    else:
      embed = discord.Embed(title='Results from Wolfram|Alpha',
                      description='Powered by Wolfram|Alpha v2.0 API',
                      url='https://www.wolframalpha.com/',
                      colour=discord.Color.red())

      embed.add_field(name='Error', value='No result found')

      # Find out why no result is availible
      if val:=res.get('didyoumeans'):
        val = val['didyoumean']
        val ='\n'.join([v['#text'] for v in val])
        embed.add_field(name='Did you mean', value=val, inline=False)
      
      elif val:=res.get('tips'):
        embed.add_field(name='Tip', value=val['tip']['@text'], inline=False)
      
      embeds.append(embed)

    paginator = PaginatorInterface(self.bot, Paginator(pages=embeds))
    await paginator.send_to(ctx)

def setup(bot):
  bot.add_cog(WebUtils(bot))