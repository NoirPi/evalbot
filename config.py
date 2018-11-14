from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

discord = config['discord']

token = discord['token']
status = discord.get('status')
