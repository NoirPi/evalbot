import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Pattern

from discord import Embed, Color, Message, Guild, TextChannel, Member
from discord.ext.commands import Bot

from compile_api import execute

CODE_BLOCK_REGEX: Pattern = re.compile("```(?P<lang>.*)\n(?P<code>[\\s\\S]*?)```")
INPUT_BLOCK_REGEX: Pattern = re.compile("input[: \t\n]*```(?P<lang>.*)?\n(?P<text>[\\s\\S]*?)```", re.IGNORECASE)

PYTHON_3 = ('python3', 2)
NODEJS = ('nodejs', 2)
C_LANG = ('c', 3)
CPP = ('cpp14', 2)
PHP = ('php', 2)
PYTHON_2 = ('python2', 1)
RUBY = ('ruby', 2)
GO_LANG = ('go', 2)
SCALA = ('scala', 2)
BASH = ('bash', 2)
CSHARP = ('csharp', 2)
HASKELL = ('haskell', 2)
BRAINFUCK = ('brainfuck', 0)
LUA = ('lua', 1)
DART = ('dart', 2)
KOTLIN = ('kotlin', 1)
JAVA = ('java', 0)

languages = {
    'kt': KOTLIN,
    'kotlin': KOTLIN,
    'dart': DART,
    'dt': DART,
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
}


class ExecuteCog(object):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.last_messaged = defaultdict(lambda: datetime.fromtimestamp(0))

    # noinspection PyMethodMayBeStatic
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
        if not author.guild_permissions.manage_messages:
            self.last_messaged[author.id] = datetime.now()
        language, version = languages[lang]
        response = await execute(code, language, version)
        if response.status_code == 429:
            return await channel.send(
                embed=Embed(
                    color=Color.blurple(),
                    description="The daily ratelimit for our API is reached. A great alternative is [Ideone]("
                                "https://ideone.com/) or [Repl.it](https://repl.it/)"))
        if response.status_code == 401:
            return await channel.send(
                embed=Embed(
                    color=Color.red(),
                    description="Our API credentials are invalid. Please contact the bot owner"))
        memory = response.memory
        output = response.output
        cpu_time = response.cpu_time
        await channel.send(
            embed=Embed(
                title="Executed your code",
                description=f"```\n{output}```"
            ).set_footer(text=f"Executed in {cpu_time}s. Memory: {memory}"))


def setup(bot: Bot):
    bot.add_cog(ExecuteCog(bot))
