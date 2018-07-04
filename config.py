from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

discord = config['discord']

token = discord['token']


jdoodle = config['jdoodle']

jdoodle_secret = jdoodle['secret']
jdoodle_id = jdoodle['id']
