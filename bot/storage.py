import datetime

from peewee import *

db = SqliteDatabase('jokes.db')
default_generated = "unknown"


class BaseModel(Model):
    class Meta:
        database = db


class Joke(BaseModel):
    joke_id = AutoField()
    text = CharField(max_length=1024)
    created_date = DateTimeField(default=datetime.datetime.now)
    generated_by = CharField(max_length=128, default=default_generated)


class Vote(BaseModel):
    joke = ForeignKeyField(Joke, backref='votes')
    user_id = CharField()
    rate = IntegerField(default=0)

    class Meta:
        primary_key = CompositeKey('joke', 'user_id')


def add_joke(text, generated_by=default_generated):
    """
    :param generated_by: where this joke came from - modelA/modelB/datasetA...
    :param text: text of joke
    :return: id of registered joke
    """
    joke = Joke.create(text=text, generated_by=generated_by)
    return joke.joke_id


def add_or_update_vote(joke_id, user_id, rating):
    # https://stackoverflow.com/questions/33485312/insert-or-update-a-peewee-record-in-python
    Vote.insert(joke_id=joke_id, user_id=user_id,
                rate=rating).on_conflict('replace').execute()


db.connect()
db.create_tables([Joke, Vote])  # Don't deletes prev data

if __name__ == '__main__':
    # Use case
    for _ in range(3):
        joke = Joke.create(text="kekv")
        for v in range(5, 10):
            Vote.create(joke_id=joke, user_id="abc" + str(v), rate=v % 2)
