import cogs.utils.configloader as configloader
discordConfig = configloader.getDiscordValues()

serverList = []
selectedServerId = -1
readyUsers = []
teamOne = []
teamTwo = []
pickNum = 1
team1VoiceChannel = None
team2VoiceChannel = None
teamOneSteamID = []
teamTwoSteamID = []
team1ApiID = -1
team2ApiID = -1
matchApiID = -1
mapList = discordConfig['vetoMapPool'].split(' ')
# Set in readysystem first, then here.
currentVeto = None
match = None
firstCaptain = None
secondCaptain = None
inProgress = False
matchApiID = -1