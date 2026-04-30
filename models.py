from peewee import *

db = SqliteDatabase('todos.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = TextField(unique=True)
    password = TextField()


class Todo(BaseModel):
    title = TextField()
    deadline = DateTimeField(null=True)
    weight = IntegerField(default=3)
    done = BooleanField(default=False)

    user = ForeignKeyField(User, backref='todos')


def init_db():
    db.connect()
    db.create_tables([User, Todo])