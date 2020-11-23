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
                    }
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
                    'ignore_server': True,
                    'max_maps': 1
                }
            ]
            retVal = requests.post(url=apiValues['get5host']+'/matches', json=myJSONMatch)
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
                    'map': mapname,
                    'team_name': teamName,
                    'pick_or_ban': pickBan
                }
            ]
            retVal = requests.post(url=apiValues['get5host']+'/vetoes', json=myVetoData)
            print(retVal.json())
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