from peewee import *
import datetime
import logging

# https://peewee.readthedocs.io/en/latest/peewee/models.html#field-types-table
# https://peewee.readthedocs.io/en/latest/peewee/relationships.html#model-definitions
db = SqliteDatabase('telegregator.db')
class BaseModel(Model):
    class Meta:
        database = db
class Contact(BaseModel):
    contact_id = IntegerField(unique=True)
    added_at = DateTimeField(default=datetime.datetime.now)
class Channel(BaseModel):
    channel_id = IntegerField(unique=True)
    channel_name = CharField(default='')
    channel_title = CharField(default='')
class Feed(BaseModel):
    feed_id = IntegerField(unique=True)
    contact = ForeignKeyField(Contact, backref='contacts')
    is_filter = BooleanField(default=True)
    is_enable = BooleanField(default=True)
    feed_title = CharField(default='')
class Forward(BaseModel):
    feed = ForeignKeyField(Feed, backref='feeds')
    channel = ForeignKeyField(Channel, backref='channels')
class Filter(BaseModel):
    word = CharField(unique=True)
    contact = ForeignKeyField(Contact, backref='contacts')

# Contact.create_table()
# Channel.create_table()
# Feed.create_table()
# Forward.create_table()
# Filter.create_table()

# db.create_tables([Contact, Channel, Forward, Feed, Filter])

# DEBUG 
# loggerdb = logging.getLogger('peewee')
# loggerdb.addHandler(logging.StreamHandler())
# loggerdb.setLevel(logging.DEBUG)

def create_tables():
    with db:
        db.create_tables([Contact, Channel, Forward, Feed, Filter])
