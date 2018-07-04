import re
from typing import List, Dict, Pattern

import discord
from discord import Embed, Color
from discord.ext import commands
from discord.ext.commands import Context as CommandContext, Bot, is_owner, command

from util import load_all_modules

REPLACEMENTS: Dict[Pattern, str] = {
    re.compile(r'<@!?(?P<id>[0-9]+)>'): '(guild.get_member({id}) if guild is not None else client.get_user({id}))',
    re.compile(r'<#(?P<id>[0-9]+)>'): '(discord.utils.get(all_channels, id={id}))',
    re.compile(r'<@&(?P<id>[0-9]+)>'): '(discord.utils.get(all_roles, id={id}))',
    # Maybe later emoji support
}


async def handle_eval(message: discord.Message, client: discord.Client, to_eval: str):
    channel: discord.TextChannel = message.channel
    author: discord.Member = message.author

    all_channels: List[discord.Guild] = []
    all_roles: List[discord.Role] = []
    for guild in client.guilds:
        guild: discord.Guild = guild  # for type hints
        all_channels += guild.channels
        all_roles += guild.roles

    variables = {
        'message': message,
        'author': author,
        'channel': channel,
        'all_channels': all_channels,
        'all_roles': all_roles,
        'client': client,
        'discord': discord,
        'print': (lambda *text: client.loop.create_task(channel.send(' '.join(text))))
    }
    if channel.guild is not None:
        variables['guild'] = channel.guild
    lines: List[str] = to_eval.strip().split('\n')
    lines[-1] = 'return ' + lines[-1]
    block: str = '\n'.join(' ' + line for line in lines)
    code = f"async def code({', '.join(variables.keys())}):\n" \
           f"{block}"

    for regex, replacement in REPLACEMENTS.items():
        code = re.sub(regex, lambda match: replacement.format(**match.groupdict()), code)

    _globals, _locals = {}, {}
    try:
        exec(code, _globals, _locals)
    except Exception as e:
        await message.channel.send(
            embed=discord.Embed(color=discord.Color.red(), description="Compiler Error: `%s`" % (str(e))))
        return
    result = {**_globals, **_locals}
    try:
        result = await result["code"](**variables)
    except Exception as e:
        await message.channel.send(
            embed=discord.Embed(color=discord.Color.red(), description="Runtime Error: `%s`" % (str(e))))
        return

    return await channel.send(
        embed=Embed(
            color=Color.red(),
            description="📥 Evaluation success: ```py\n%r\n```" % result))


class AdminCog(object):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @command()
    @is_owner()
    async def eval(self, ctx: CommandContext, *, to_eval: str = None):
        if to_eval is None:
            return await ctx.send(
                embed=Embed(
                    description="<Insert generic insult about your stupidity here>",
                    color=Color.red()))
        await handle_eval(ctx.message, self.bot, to_eval)

    async def on_ready(self):
        print('-' * 50)
        print('Name:   ' + self.bot.user.name)
        print('Guilds: ' + ', '.join(guild.name for guild in self.bot.guilds))
        print('-' * 50)

    @command()
    @is_owner()
    async def reload(self, ctx: CommandContext, *extensions):
        for extension in (extensions or self.bot.extensions.copy().keys()):
            self.bot.unload_extension(extension)
        await ctx.send(
            embed=Embed(
                color=Color.red(),
                description='Unloaded extensions', ))
        if len(extensions) == 0:
            load_all_modules(self.bot)
        else:
            for extension in extensions:
                try:
                    self.bot.load_extension(extension)
                except:
                    await ctx.send(
                        embed=Embed(
                            title=f"Failed to load module `{extension}`",
                            color=Color.red()))
        await ctx.send(
            embed=Embed(
                title=f"Reloaded {len(extensions) or len(self.bot.extensions)} extension(s)",
                color=Color.green()))


def setup(bot: Bot):
    bot.add_cog(AdminCog(bot))
