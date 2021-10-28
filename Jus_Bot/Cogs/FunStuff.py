from discord.ext import commands, tasks
from ..Utils import TriviaClient, ChoiceView, categories, embed_template
from ..PythonShell import replChannel
import asyncio
import base64
import discord
import random
import signal
class FunStuff(commands.Cog):
  """> Place with fun, wacky stuff"""

  def __init__(self, bot):
    self.bot = bot
    self.hidden = False
    self.suppress = False
    self.trivia_client = TriviaClient()
    self.update_token.start()

  @tasks.loop(hours=1)
  async def update_token(self):
    await self.trivia_client.update_token()

  def cog_unload(self):
    self.update_token.cancel()

  @commands.command(help='> Don\'t even try')
  @commands.is_owner()
  async def repl(self, ctx):
    handler = replChannel(self.bot, ctx)
    returncode = await handler.start_repl()
    if returncode == signal.SIGTERM:
      await ctx.reply('The repl timed out or was terminated')

  #rng stuff
  @commands.command(help='> Gives you a random number or something idk')
  async def rng(self, ctx, start: int, end: int):
      if start < end:
        await ctx.reply(str(random.randrange(start,end)))
      else:
        await ctx.reply('Start range cannot be more than the end of it')
  
  @commands.command(help='> Imagine rng, but only from 1 to 6')
  async def dice(self, ctx):
    await ctx.reply(random.randint(1,6))
  
  #other stuff
  @commands.command(help='> I have no idea what this does so have fun')
  async def decode(self, ctx, *, args):
    text = args.split()[:-1]
    decoder = args.split()[-1]
    try:
      await ctx.reply(text.decode(decoder))
    except:
      await ctx.reply('Unable to decode text')
  
  @commands.command(help='> Allows anyone to execute code on the bot, this is perfectly safe')
  async def pyeval(self, ctx):
    class View(discord.ui.View):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        button = discord.ui.Button(style=discord.ButtonStyle.secondary, label='Go here I guess',url='https://Puzzles.juscodin.repl.co/puzzle-1')
        self.add_item(button)
    await ctx.reply('Hah nice try', view=View())

  @commands.command(help='> This is pain')
  async def trivia(self, ctx, amount: int, difficulty=None, type=None):

    async def handler(select, interaction):
      global score
      score = 0
      category = categories[select.values[0]]
      await interaction.response.defer()
      select.view.stop()

      questions = await self.trivia_client.trivia(amount, category=category, difficulty=difficulty, type=type)
      for question in questions:
        cate = base64.b64decode(question['category']).decode('utf-8')
        qdiff= base64.b64decode(question['difficulty']).decode('utf-8')
        qtext = base64.b64decode(question['question']).decode('utf-8')
        correct = base64.b64decode(question['correct_answer']).decode('utf-8')
        wrong = list(map(lambda a: base64.b64decode(a).decode('utf-8'), question['incorrect_answers']))
        embed = embed_template(ctx, title='Trivia', description='Powered by OpenTriviaDatabase')
        embed.add_field(name='Question', value=qtext, inline=False)
        embed.add_field(name='Category', value=cate)
        embed.add_field(name='Difficulty', value=qdiff.title())

        options = wrong + [correct]
        random.shuffle(options)
        choices = [discord.SelectOption(label=l) for l in options]

        async def handle_answer(select, interaction):
          global score
          answer = select.values[0]
          embed = embed_template(ctx)
          if answer == correct:
            embed.title, embed.description = 'Correct!', 'I actually dk what to put here lol'
            embed.colour = discord.Colour.brand_green()
            score += 1
          else:
            embed.title, embed.description = 'Wrong!', f'The correct answer was {correct}'
            embed.colour = discord.Colour.brand_red()
          await select.view.message.edit(embed=embed, view=None)
          select.view.stop()

        view = ChoiceView(choices, handle_answer, timeout=10.0)

        view.user = interaction.user
        view.message = select.view.message
        await select.view.message.edit(content=None, embed=embed, view=view)

        is_timeout = await view.wait()
        if is_timeout:
          await asyncio.sleep(0.1)
          embed = embed_template(ctx)
          embed.title, embed.description = 'Too slow!', 'Answer the question within 10 seconds'
          embed.colour = discord.Colour.brand_red()
          await select.view.message.edit(embed=embed, view=None)

        await asyncio.sleep(3)
      
      embed = embed_template(ctx, title='Score', description=f'You scored {score}/{amount}')
      await select.view.message.edit(embed=embed, view=None)

    choices = [discord.SelectOption(label=l) for l in categories.keys()]

    view = ChoiceView(choices, handler, timeout=15.0)
    await view.send_to(ctx, content='Please select a category')

def setup(bot):
  bot.add_cog(FunStuff(bot))