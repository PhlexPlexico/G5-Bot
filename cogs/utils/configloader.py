import configparser

config = configparser.ConfigParser()
config.read('settings.ini')

def __init__(self, config):
    self.config = config

def getDatabaseValues():
    return config['DATABASE']

def getDiscordValues():
    return config['DISCORD']