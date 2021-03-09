import asyncio
import requests
import sqlite3
import datetime
import cogs.utils.configloader as config

apiValues = config.getAPIValues()

def tryAuth():
    try:
        myJSONAuth = [
            {
                'user_id': apiValues['userID'],
                'user_api': apiValues['userKey']
            }
        ]
        retVal = requests.request(method='get', url=apiValues['get5host'], json=myJSONAuth)
        if ("/auth/steam" in retVal.url):
            raise Exception("Login failed.")
        return True
    except:
        print("Some other error has happened, oh dear.")
        return False

def createTeam(teamName, captain_id, captain_name):
    if (tryAuth):
        try:
            db = sqlite3.connect(r"./steam_auths.db")
            steamCur = db.cursor()
            steamCur.execute("SELECT steam_id FROM steam_auth WHERE discord_id = ?;", [captain_id])
            steamId = steamCur.fetchone()[0]
            myJSONTeam = [
                {
                    'user_id': apiValues['userID'],
                    'user_api': apiValues['userKey'],
                    'name': teamName,
                    'public_team': 0,
                    'auth_name': {
                        steamId: {
                            'name': captain_name,
                            'captain': 1
                        }
                    },
                    'flag': 'CA'
                }
            ]
            retVal = requests.post(url=apiValues['get5host']+'/teams', json=myJSONTeam)
            return retVal.json()['id']
        except Exception as error:
            print('Error!!! ', error)
            return -1

def addPlayer(teamId, discord_id, name):
    if(tryAuth):
        try:
            db = sqlite3.connect(r"./steam_auths.db")
            steamCur = db.cursor()
            steamCur.execute("SELECT steam_id FROM steam_auth WHERE discord_id = ?;", [discord_id])
            steamId = steamCur.fetchone()[0]
            myJSONTeam = [
                {
                    'id': teamId,
                    'user_id': apiValues['userID'],
                    'user_api': apiValues['userKey'],
                    'auth_name': {
                        steamId: {
                            'name': name
                        }
                    }
                }
            ]
            retVal = requests.request(method='put', url=apiValues['get5host']+'/teams', json=myJSONTeam)
            if (retVal.status_code != 200):
                print(retVal.json())
                return -1
            return True
        except:
            print('Error!!!')
            return False

# Delete a team if we cancel or finish before a pug finishes.
def deleteTeam(teamID):
    if (tryAuth):
        try:
            myJSONDelete = [
                {
                    'user_id': apiValues['userID'],
                    'user_api': apiValues['userKey'],
                    'team_id': teamID
                }
            ]
            retVal = requests.request(method='delete', url=apiValues['get5host']+'/teams', json=myJSONDelete)
            if (retVal.status_code != 200):
                raise Exception("We failed to delete the team.")
            return True
        except Exception as error:
            print(error)
            return False

def createMatch(team1id, team2id):
    if(tryAuth):
        try:
            myJSONMatch = [
                {
                    'user_id': apiValues['userID'],
                    'user_api': apiValues['userKey'],
                    'team1_id': team1id,
                    'team2_id': team2id,
                    'title': '[PUG] Map {MAPNUMBER} of {MAXMAPS}',
                    'is_pug': 1,
                    'start_time': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    'ignore_server': 1,
                    'max_maps': 1,
                    'veto_first': 'team1'
                }
            ]
            retVal = requests.post(url=apiValues['get5host']+'/matches', json=myJSONMatch)
            if (retVal.status_code != 200):
                print(retVal.json())
                return -1
            return retVal.json()['id']
        except Exception as error:
            print(error)
            return -1

def vetoMap(mapname, teamName, matchid, pickBan):
    if(tryAuth):
        try:
            myVetoData = [
                {
                    'user_id': apiValues['userID'],
                    'user_api': apiValues['userKey'],
                    'match_id': matchid,
                    'map_name': mapname,
                    'team_name': teamName,
                    'pick_or_ban': pickBan
                }
            ]
            retVal = requests.post(url=apiValues['get5host']+'/vetoes', json=myVetoData)
            if (retVal.status_code != 200):
                print(retVal.json())
                return -1
            return retVal.json()['id']
        except Exception as error:
            print(error)
            return -1

def deleteVetoes(matchid):
    if (tryAuth):
        try:
            myJSONDelete = [
                {
                    'user_id': apiValues['userID'],
                    'user_api': apiValues['userKey'],
                    'match_id': matchid
                }
            ]
            retVal = requests.request(method='delete', url=apiValues['get5host']+'/vetoes', json=myJSONDelete)
            if (retVal.status_code != 200):
                raise Exception("We failed to delete the vetoes.")
            return True
        except Exception as error:
            print(error)
            return False

def cancelMatch(matchid):
    if (tryAuth):
        try:
            myJSONDelete = [
                {
                    'user_id': apiValues['userID'],
                    'user_api': apiValues['userKey']
                }
            ]
            retVal = requests.request(method='get', url=apiValues['get5host']+'/matches/'+str(matchid)+'/cancel', json=myJSONDelete)
            if (retVal.status_code != 200):
                raise Exception("We failed to cancel the match.")
            return True
        except Exception as error:
            print(error)
            return False

def getAvailablePublicServers():
    if (tryAuth):
        try:
            retVal = requests.request(method='get', url=apiValues['get5host']+'/servers/available')
            if (retVal.status_code != 200):
                raise Exception("We failed to retrieve servers")
            return retVal.json()['servers']
        except Exception as error:
            print(error)
            return []

def getListedServers():
    if (tryAuth):
        try:
            myJSONInfo = [
                {
                    'user_id': apiValues['userID'],
                    'user_api': apiValues['userKey']
                }
            ]
            allServers = []
            for serverId in apiValues['serverIDs'].split(','):
                retVal = requests.request(method='get', url=apiValues['get5host']+'/servers/'+str(serverId), json=myJSONInfo)
                if (retVal.status_code == 200 and retVal.json()['server']['in_use'] == 0):
                    allServers.append(retVal.json()['server'])
            return allServers
        except Exception as error:
            print(error)
            return []

def assignServer(matchid, serverid):
    if(tryAuth):
        try:
            myJSONMatch = [
                {
                    'user_id': apiValues['userID'],
                    'user_api': apiValues['userKey'],
                    'server_id': serverid,
                    'match_id': matchid
                }
            ]
            retVal = requests.request(method='put', url=apiValues['get5host']+'/matches', json=myJSONMatch)
            if (retVal.status_code != 200):
                print(retVal.json())
                return False
            return True
        except Exception as error:
            print(error)
            return False