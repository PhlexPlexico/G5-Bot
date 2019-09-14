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


def get_available_public_servers():
    servers = Game_server.select().where((Game_server.public_server == 1)
                                         & (Game_server.in_use == 0)).get()
    return servers


def get_server(server_id):
    server = Game_server.get(server_id)
    return server

def create_match(user_id, server_id, veto_first):
    api_key = ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(24))
    match = Match.create(user_id=user_id, server_id=server_id, team1_id=int(databaseValues['team1ScrimID']), team2_id=int(
        databaseValues['team2ScrimID']), skip_veto=True, api_key=api_key, veto_mappool=discordValues['vetoMapPool'], season_id=int(databaseValues['seasonID']), veto_first=veto_first, enforce_teams=False)
    match.save()
    return match

def delete_match(match_id):
    match = Match.get(match_id)
    match.delete_instance()
    return

def create_veto(match_id, team_name, mapName, pick_or_veto):
    veto = Veto.create(match_id=match_id, team_name=team_name,
                       map=mapName, pick_or_veto=pick_or_veto)
    veto.save()
    return veto

def delete_vetoes(match_id):
    Veto.delete().where(match_id==match_id)
    return

def update_match_first_veto(match_id, firstVeto):
    match = Match.select().where(Match.id == match_id).get()
    match.veto_first = firstVeto
    match.save()
    return


def update_match_maps(match_id, mappool):
    match = Match.select().where(Match.id == match_id).get()
    match.veto_mappool = mappool
    match.save()
    return


class BaseModel(pw.Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = db


class User(BaseModel):
    id = pw.AutoField(primary_key=True)
    steam_id = pw.CharField(max_length=40, unique=True)
    name = pw.CharField(max_length=40)
    admin = pw.BooleanField(default=False)
    super_admin = pw.BooleanField(default=False)


class Season(BaseModel):
    id = pw.AutoField()
    user_id = pw.ForeignKeyField(User, index=True)
    name = pw.CharField(max_length=32)
    start_date = pw.DateTimeField()
    end_date = pw.DateTimeField()


class Game_server(BaseModel):
    id = pw.AutoField()
    user_id = pw.ForeignKeyField(User, backref='id', index=True)
    in_use = pw.SmallIntegerField()
    ip_string = pw.CharField(max_length=32)
    port = pw.IntegerField()
    rcon_password = pw.CharField(max_length=128)
    display_name = pw.CharField(max_length=32)
    public_server = pw.BooleanField(default=False)


class Match(BaseModel):
    id = pw.AutoField()
    user_id = pw.IntegerField(default=1, index=True)
    server_id = pw.ForeignKeyField(Game_server, backref='id', index=True)
    team1_id = pw.IntegerField(
        default=databaseValues['team1ScrimID'], index=True)
    team2_id = pw.IntegerField(
        default=databaseValues['team2ScrimID'], index=True)
    title = pw.CharField(max_length=60, default='Map {MAPNUMBER} of {MAXMAPS}')
    skip_veto = pw.BooleanField(default=True)
    api_key = pw.CharField(max_length=32)
    veto_mappool = pw.CharField(max_length=500)
    season_id = pw.ForeignKeyField(Season, backref='id', index=True)
    veto_first = pw.CharField(max_length=5)
    enforce_teams = pw.BooleanField(default=False)
    max_maps = pw.IntegerField(default=1)
    side_type = pw.CharField(max_length=32, default='standard')
    private_match = pw.BooleanField(default=False)
    cancelled = pw.BooleanField(default=False)


class Veto(BaseModel):
    id = pw.AutoField()
    match_id = pw.IntegerField()
    team_name = pw.CharField(max_length=64)
    map = pw.CharField(max_length=32)
    pick_or_veto = pw.CharField(max_length=4)


db.connect()
