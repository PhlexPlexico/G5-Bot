import asyncio
import requests
import cogs.utils.configloader as config

apiValues = config.getAPIValues()

def tryAuth():
    try:
        myJSONAuth = [{'user_id': apiValues['userID'], 'user_api': apiValues['userKey']}]
        retVal = requests.request(method='get', url=apiValues['get5host'], json=myJSONAuth)
        if ("/auth/steam" in retVal.url):
            raise Exception("Login failed.")
        return True
    except:
        print("Some other error has happened, oh dear.")
        return False

def createTeam(teamName):
    if (tryAuth):
        try:
            myJSONTeam = [{'user_id': apiValues['userID'], 'user_api': apiValues['userKey'], 'name': teamName, 'public_team': 0}]
            retVal = requests.post(url=apiValues['get5host']+'/teams', json=myJSONTeam)
            print(retVal.json()['id'])
            return retVal.json()['id']
        except:
            print('Error!!!')
            return -1

# Delete a team if we cancel or finish before a pug finishes.
def deleteTeam(teamID):
    if (tryAuth):
        try:
            myJSONDelete = [{'user_id': apiValues['userID'], 'user_api': apiValues['userKey'], 'team_id': teamID}]
            retVal = requests.request(method='delete', url=apiValues['get5host']+'/teams', json=myJSONDelete)
            if (retVal.status_code != 200)
                raise Exception("We failed to delete the team.")
            return True
        except Exception as error:
            print(error)
            return False