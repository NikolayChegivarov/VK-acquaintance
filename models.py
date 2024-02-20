import sqlalchemy as sq
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Sender(Base):
    __tablename__ = "sender"
    __table_args__ = {'schema': 'pretenders'}
    id_sender = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    First_Name_Last_Name = sq.Column(sq.String(length=40), unique=True)
    vk_id = sq.Column(sq.Integer, nullable=False)
    link = sq.Column(sq.String(length=40), unique=True)

    def __str__(self):
        return f'Отправитель {self.vk_id}: {self.First_Name_Last_Name}'

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'pretenders'}
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, unique=True, nullable=False)

    def __str__(self):
        return f'id: {self.id}, user_id: {self.user_id}'

class Favorite_users(Base):
    __tablename__ = 'favorite_users'
    __table_args__ = {'schema': 'pretenders'}
    id = sq.Column(sq.Integer, primary_key=True)
    vk_user = sq.Column(sq.Integer, sq.ForeignKey(User.id), nullable=False)
    name = sq.Column(sq.String(length=100), nullable=False)
    link = sq.Column(sq.String(250), nullable=False)

    def __str__(self):
        return (f'id: {self.id}, user_id: {self.vk_user}, name:{self.name}')

class Black_list(Base):
    __tablename__ = 'black_list'
    __table_args__ = {'schema': 'pretenders'}
    id = sq.Column(sq.Integer, primary_key=True)
    vk_user = sq.Column(sq.Integer, sq.ForeignKey(User.id), nullable=False)

    def __str__(self):
        return (f'id: {self.id}, user_id: {self.vk_user}')


