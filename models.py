import sqlalchemy as sq
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Users(Base):
    """Все потенциальные партнеры."""
    __tablename__ = 'users'
    __table_args__ = {'schema': 'pretenders'}
    user_id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True, nullable=False)
    name = sq.Column(sq.String(length=100), nullable=False)
    link = sq.Column(sq.String(250), nullable=False)
    print('Создана юзерс.')
    def __str__(self):
        return f'id: {self.id}, user_id: {self.user_id}'

class Favorite_users(Base):
    """Избранные."""
    __tablename__ = 'favorite_users'
    __table_args__ = {'schema': 'pretenders'}
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, sq.ForeignKey('pretenders.users.vk_id'), nullable=False)

    def __str__(self):
        return (f'id: {self.id}, user_id: {self.vk_user}, name:{self.name}')

class Black_list(Base):
    """Отвергнутые"""
    __tablename__ = 'black_list'
    __table_args__ = {'schema': 'pretenders'}
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_user = sq.Column(sq.Integer, sq.ForeignKey('pretenders.users.vk_id'), nullable=False)

    def __str__(self):
        return (f'id: {self.id}, user_id: {self.vk_user}')
