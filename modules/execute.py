import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Pattern

from discord import Embed, Guild, Member, Message, TextChannel
from discord.ext import commands
from discord.ext.commands import Bot

from compile_api import execute

CODE_BLOCK_REGEX: Pattern = re.compile("```(?P<lang>.*)\n(?P<code>[\\s\\S]*?)```")
INPUT_BLOCK_REGEX: Pattern = \
    re.compile("input[: \t\n]*```(?P<lang>.*)?\n(?P<text>[\\s\\S]*?)```", re.IGNORECASE)

PYTHON_3 = 24
NODEJS = 17
C_LANG = 6
CPP = 7
PHP = 8
PYTHON_2 = 5
RUBY = 12
GO_LANG = 20
SCALA = 21
BASH = 38
CSHARP = 1
HASKELL = 11
BRAINFUCK = 44
LUA = 14
KOTLIN = 43
JAVA = 4
R_LANG = 31

languages = {
    'r': R_LANG,
    'rlang': R_LANG,
    'kt': KOTLIN,
    'kotlin': KOTLIN,
    'lua': LUA,
    'py': PYTHON_3,
    'python': PYTHON_3,
    'js': NODEJS,
    'javascript': NODEJS,
    'c': C_LANG,
    'c++': CPP,
    'cpp': CPP,
    'py2': PYTHON_2,
    'go': GO_LANG,
    'scala': SCALA,
    'sc': SCALA,
    'bash': BASH,
    'hs': HASKELL,
    'haskell': HASKELL,
    'brainfuck': BRAINFUCK,
    'bf': BRAINFUCK,
    'java': JAVA,
    'php': PHP,
}


class ExecuteCog(commands.Cog, object):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.last_messaged = defaultdict(lambda: datetime.fromtimestamp(0))

    # noinspection PyMethodMayBeStatic
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.guild is None:
            return
        content: str = message.content
        guild: Guild = message.guild
        author: Member = message.author
        channel: TextChannel = message.channel
        if guild.me not in message.mentions:
            return
        code = ""
        lang = ""
        for match in CODE_BLOCK_REGEX.finditer(content):
            code = match.group('code')
            lang = match.group('lang')
            break
        if lang is "" or code is "":
            return
        inp = ""
        for match in INPUT_BLOCK_REGEX.finditer(content):
            inp += match.group("text") + '\n'
        last = self.last_messaged[author.id]
        delta = datetime.now() - last
        if delta < timedelta(seconds=30):
            return await channel.send(
                embed=Embed(
                    description=f"You are not allowed to eval code again. Check again in "
                                f"{(timedelta(seconds=30)-delta).seconds}secs"))
        if not author.guild_permissions.manage_messages and not author.id == 280766063472541697:
            self.last_messaged[author.id] = datetime.now()
        language = languages[lang]
        print(language)
        response = await execute(code, language)
        output = response.output
        stats = response.stats
        warnings = response.warnings
        errors = response.errors
        files = response.discord_files
        em = Embed(
            title="Executed your code",
            description=f"```\n{output}```"
        ).set_footer(text=stats)
        if warnings:
            em.add_field(name="Warnings", value=f'```\n{warnings}```')
        if errors:
            em.add_field(name="Errors", value=f'```\n{errors}```')
        await channel.send(
            embed=em,
            files=files if len(files) > 0 else None
        )


def setup(bot: Bot):
    bot.add_cog(ExecuteCog(bot))
