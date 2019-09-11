import peewee as pw
import configparser

config = configparser.ConfigParser()
config.read('settings.ini')

db = pw.MySQLDatabase(database=config['DATABASE']['dbname'], host=config['DATABASE']['host'], port=int(
    config['DATABASE']['port']), user=config['DATABASE']['user'], passwd=config['DATABASE']['password'])


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
        default=config['DISCORD']['team1ScrimID'], index=True)
    team2_id = pw.IntegerField(
        default=config['DISCORD']['team2ScrimID'], index=True)
    title = pw.CharField(max_length=60, default='Map {MAPNUMBER} of {MAXMAPS}')
    skip_veto = pw.BooleanField(default=True)
    api_key = pw.CharField(max_length=32)
    veto_mappool = pw.CharField(max_length=500)
    season_id = pw.ForeignKeyField(Season, backref='id', index=True)
    veto_first = pw.CharField(default=5)
    enforce_teams = pw.BooleanField(default=False)


db.connect()
