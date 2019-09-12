import peewee as pw
import cogs.utils.configloader as config
import random
import string

databaseValues = config.getDatabaseValues()
discordValues = config.getDiscordValues()
try:
    db = pw.MySQLDatabase(database=databaseValues['dbname'], host=databaseValues['host'], port=int(
        databaseValues['port']), user=databaseValues['user'], passwd=databaseValues['password'])
except:
    raise ImportError("Database is not instantiated!")


def create_match(user_id, server_id, veto_first):
    api_key = ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(24))
    match = Match.create(user_id=user_id, server_id=server_id, team1_id=int(databaseValues['team1ScrimID']), team2_id=int(
        databaseValues['team2ScrimID']), skip_veto=True, api_key=api_key, veto_mappool=discordValues['vetoMapPool'], season_id=int(databaseValues['seasonID']), veto_first='team1', enforce_teams=False)
    match.save()
    return match

def get_available_public_servers():
    servers =  Server.select().where((Server.public_server==1) & (Server.in_use==0))
    return servers

class BaseModel(pw.Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = db


class User(BaseModel):
    id = pw.AutoField
    steam_id = pw.CharField(max_length=40, unique=True)
    name = pw.CharField(max_length=40)
    admin = pw.BooleanField(default=False)
    super_admin = pw.BooleanField(default=False)


class Season(BaseModel):
    id = pw.AutoField()
    user_id = pw.ForeignKeyField(User, backref='id', index=True)
    name = pw.CharField(max_length=32)
    start_date = pw.DateTimeField()
    end_date = pw.DateTimeField()


class Server(BaseModel):
    id = pw.AutoField
    user_id = pw.ForeignKeyField(User, backref='id', index=True)
    in_use = pw.BooleanField(default=False)
    ip_string = pw.CharField(max_length=32)
    port = pw.IntegerField()
    rcon_password = pw.CharField(max_length=128)
    display_name = pw.CharField(max_length=32)
    public_server = pw.BooleanField(default=False)

    class Meta:
        table_name = 'game_server'


class Match(BaseModel):
    id = pw.AutoField()
    user_id = pw.IntegerField(default=1, index=True)
    server_id = pw.ForeignKeyField(Server, backref='id', index=True)
    team1_id = pw.IntegerField(
        default=databaseValues['team1ScrimID'], index=True)
    team2_id = pw.IntegerField(
        default=databaseValues['team2ScrimID'], index=True)
    title = pw.CharField(max_length=60, default='Map {MAPNUMBER} of {MAXMAPS}')
    skip_veto = pw.BooleanField(default=True)
    api_key = pw.CharField(max_length=32)
    veto_mappool = pw.CharField(max_length=500)
    season_id = pw.ForeignKeyField(Season, backref='id', index=True)
    veto_first = pw.CharField(default=5)
    enforce_teams = pw.BooleanField(default=False)


db.connect()
