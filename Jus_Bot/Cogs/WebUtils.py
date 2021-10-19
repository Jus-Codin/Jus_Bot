import discord
from discord.ext import commands
from datetime import timedelta
from pyowm import OWM
from pycountry import countries
from ..Utils import WolframClient, PaginatorView, Paginator, embed_template, error_template, error_handler
import os

class InvalidCountry(Exception):
  pass

class InvalidCity(Exception):
  pass

class WebUtils(commands.Cog):
  """> Commands to get info from the internet"""

  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.hidden = False
    self.suppress = False
    self.wolfram_client = WolframClient(os.getenv('APPID'))
    self.owm = OWM(os.getenv('WEATHERTOKEN'))

  @commands.command(help='> Search something up on WolframAlpha')
  async def wolfram(self, ctx, *, args):
    embeds = []
    async with ctx.typing(): 
      res = await self.wolfram_client.query(args)
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
          embed = embed_template(ctx, title='Results from Wolfram|Alpha',
                                description='Powered by Wolfram|Alpha v2.0 API',
                                url='https://www.wolframalpha.com/',
                                colour=discord.Color.orange())
          embed.add_field(name='Assumption', value=assumption)
          if warnings:
            embed.add_field(name='Warnings', value='\n'.join(warnings))
          embeds.append({'embeds':[embed.add_field(name=pod.title, value=pod.text, inline=False)]})
    
    else:
      embed = error_template(ctx, title='Results from Wolfram|Alpha',
                      description='Powered by Wolfram|Alpha v2.0 API',
                      url='https://www.wolframalpha.com/')

      embed.add_field(name='Error', value='No result found')

      # Find out why no result is availible
      if val:=res.get('didyoumeans'):
        val = val['didyoumean']
        try:
          val ='\n'.join([v['#text'] for v in val])
        except TypeError:
          val = val['#text']
        embed.add_field(name='Did you mean', value=val, inline=False)
      
      elif val:=res.get('tips'):
        embed.add_field(name='Tip', value=val['tip']['@text'], inline=False)
      
      embeds.append({'embeds':[embed]})

    paginator = PaginatorView(Paginator(pages=embeds))
    await paginator.send_to(ctx)

  @commands.command()
  async def weather(self, ctx, city, country=None):
    async with ctx.typing():
      reg = self.owm.city_id_registry()
      if country:
        country = countries.get(name=country.title())
        if country is None:
          raise InvalidCountry()
        else:
          ids = reg.ids_for(city.title(), country.alpha_2)
      else:
        ids = reg.ids_for(city.title())
      if ids:
        id = ids[0][0]
      else:
        raise InvalidCity()
        
      mng = self.owm.weather_manager()
      weather = mng.weather_at_id(id).weather

    main = weather.status
    spec = weather.detailed_status

    icon_url = weather.weather_icon_url(size='2x')

    humidity = weather.humidity

    temp = weather.temperature('celsius')
    temp_min = temp['temp_min']
    temp_max = temp['temp_max']
    temp = temp['temp']
    
    temp_message = [
      f'Current temperature: {temp}°C',
      f'Minimum temperature: {temp_min}°C',
      f'Maximum temperature: {temp_max}°C'
    ]

    wind = weather.wind()
    wind_speed = wind['speed']
    wind_deg = wind['deg']

    wind_message = [
      f'Speed: {wind_speed} m/s',
      f'Bearing: {wind_deg:03d}'
    ]

    offset = timedelta(seconds=weather.utc_offset)

    sunrise = (weather.sunrise_time('date')+offset).strftime('%I:%M:%S%p local time')
    sunset = (weather.sunset_time('date')+offset).strftime('%I:%M:%S%p local time')

    title = f'Weather at {city.title()}'
    if country:
      title += ', ' + country

    embed = embed_template(ctx, title=title, description='Powered by OpenWeatherMap', url='https://openweathermap.org/')
    embed.set_thumbnail(url=icon_url)
    embed.add_field(name=main, value=spec.title())
    embed.add_field(name='Humidity', value=f'{humidity}%', inline=False)
    embed.add_field(name='Wind', value='\n'.join(wind_message))
    embed.add_field(name='Sunrise', value=f'Sunrise at {sunrise}')
    embed.add_field(name='Sunset', value=f'Sunset at {sunset}')
    embed.add_field(name='Current Temperature', value=f'{temp}°C')
    embed.add_field(name='Minimum Temperature', value=f'{temp_min}°C')
    embed.add_field(name='Maximum Temperature', value=f'{temp_max}°C')

    await ctx.send(embed=embed)
  
  @weather.error
  async def handler(self, ctx, error):
    if isinstance(error, commands.CommandInvokeError):
      error = error.original
      if isinstance(error, InvalidCity):
        embed = error_template(ctx, description='Could not find the requested city.')
        await ctx.send(embed=embed)
      elif isinstance(error, InvalidCountry):
        embed = error_template(ctx, description='Could not fine the requested country.')
        await ctx.send(embed=embed)
    else:
      await error_handler(ctx, error)

def setup(bot):
  bot.add_cog(WebUtils(bot))