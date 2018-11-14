from discord import Game
from discord.ext.commands import Bot, when_mentioned_or

from config import token, status
from util import load_all_modules

bot = Bot(command_prefix=when_mentioned_or('!'), activity=Game(status) if status else None)

load_all_modules(bot)

if __name__ == '__main__':
    bot.run(token)
