import os

from discord.ext.commands import Bot


def load_all_modules(bot: Bot, module_folder='modules', module_package=None):
    if module_package is None:
        module_package = module_folder.replace('/', '.')
    for module in os.listdir(module_folder):
        if module.endswith('.py') and not module.startswith('_'):
            bot.load_extension(module_package + '.' + module[:-3])
