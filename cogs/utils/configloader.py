import configparser

config = configparser.ConfigParser()
config.read('settings.ini')

def __init__(self, config):
    self.config = config

def getAPIValues():
    return config['API']

def getDiscordValues():
    return config['DISCORD']