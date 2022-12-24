from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext.commands import Cog, Context, command

from ..ui.paginator import Paginator, Page
from ..utils import embed_template, error_template
from ..wolfram import AsyncClient

import discord

if TYPE_CHECKING:
  from ..bot import JusBot

class WolframAlpha(Cog):
  """Get useful information from the Wolfram|Alpha v2.0 API"""

  def __init__(self, bot: JusBot, hidden: bool, suppress: bool):
    self.bot = bot
    self.hidden = hidden
    self.suppress = suppress
    self.appid = bot.wolfram_appid
    self.client = AsyncClient(self.appid)

  @command(help="Search up something using the Wolfram|Alpha API")
  async def wolfram(self, ctx: Context, *, text):
    async with ctx.typing():
      try:
        res = await self.client.full_results_query(text)
      except AttributeError:
        return

    embeds = []
    if res.success:

      if res.assumptions is None:
        assumption = "None"
      else:
        assumption = res.assumptions.text
        embed = embed_template(
          self.bot, ctx.author,
          title="Results from Wolfram|Alpha",
          description="Powered by Wolfram|Alpha v2.0 API",
          url="https://www.wolframalpha.com/",
          colour=discord.Color.orange()
        )
        embed.add_field(name="Assumption", value=assumption)

        if res.warnings is not None:
          embed.add_field(
            name="Warning:",
            value="\n".join(w.msg for w in res.warnings),
            inline=False
          )

        if res.generalization is not None:
          embed.add_field(
            name=res.generalization.desc,
            value=res.generalization.topic,
            inline=False
          )

        embeds.append(embed)

      primary = None
      for pod in res.pods:
        if pod.text:
          embed = embed_template(
            self.bot, ctx.author,
            title=pod.title,
            description=pod.text,
            colour=discord.Color.orange()
          ).set_author(
            name="Powered by Wolfram|Alpha v2.0 API",
            url="https://wolframalpha.com/",
            icon_url=self.bot.user.display_avatar.url
          )
          if pod.primary:
            primary = embed
          else:
            embeds.append(embed)

      if primary is not None:
        embeds.insert(1, primary)

      paginator = Paginator(
        pages=[
          Page(embed=embed) 
          for embed in embeds
        ]
      )

      return await paginator.send_to(ctx)

    elif res.is_fallthrough:
      embed = error_template(
            self.bot, ctx.author,
            title="Error",
            description="No result found",
            colour=discord.Color.orange()
          ).set_author(
            name="Powered by Wolfram|Alpha v2.0 API",
            url="https://wolframalpha.com/",
            icon_url=self.bot.user.display_avatar.url
          )

      if res.didyoumeans is not None:
        embed.add_field(
          name="Did you mean:",
          value="\n".join(f"`{i.val}`" for i in res.didyoumeans)
        )

      elif res.tips is not None:
        embed.add_field(
          name="Tip:",
          value="\n".join(t.text for t in res.tips)
        )
      
      elif res.examplepage is not None:
        embed.add_field(
          name="Refer to this website:",
          value=res.examplepage.url
        )

      else:
        embed.description = res.fallthrough.msg

    elif res.is_error:
      embed = error_template(
        self.bot, ctx.author,
        title="Error",
        description="An internal error has occurred, please try again later",
        colour=discord.Color.orange()
      ).set_author(
        name="Powered by Wolfram|Alpha v2.0 API",
        url="https://wolframalpha.com/",
        icon_url=self.bot.user.display_avatar.url
      )

      print(res.raw)
      
    
    else:
      embed = error_template(
        self.bot, ctx.author,
        title="Error",
        description="No result found",
        colour=discord.Color.orange()
      ).set_author(
        name="Powered by Wolfram|Alpha v2.0 API",
        url="https://wolframalpha.com/",
        icon_url=self.bot.user.display_avatar.url
      )
      
    await ctx.send(embed=embed)