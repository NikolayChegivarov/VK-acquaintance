import sqlalchemy as sq
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Bot_users
class BotUsers(Base):
    """Пользователи бота."""
    __tablename__ = 'bot_users'
    __table_args__ = {'schema': 'pretenders'}
    id_bot_user = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    id_vk_user = sq.Column(sq.Integer, nullable=False)
    user_name = sq.Column(sq.String(length=100), nullable=False)

    def __str__(self):
        return f'id_bot_user: {self.id_bot_user}, user_name: {self.user_name}'


class Users_potential(Base):
    """Все потенциальные партнеры найденные по критериям юзера бота."""
    __tablename__ = 'users_potential'
    __table_args__ = {'schema': 'pretenders'}
    id_user_potential = sq.Column(sq.Integer, autoincrement=True)
    id_bot_user = sq.Column(sq.Integer, sq.ForeignKey('pretenders.bot_users.id_bot_user'), nullable=False)
    id_vk_user = sq.Column(sq.Integer, primary_key=True, nullable=False)
    user_name = sq.Column(sq.String(length=100), nullable=False)
    link = sq.Column(sq.String(250), nullable=False)

    def __str__(self):
        return f'id_users_potential: {self.id_users_potential}, user_name: {self.user_name}'


class Favorite_users(Base):
    """Избранные пользователи."""
    __tablename__ = 'favorite_users'
    __table_args__ = {'schema': 'pretenders'}
    id_favorite_user = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    id_vk_user = sq.Column(sq.Integer, sq.ForeignKey('pretenders.users_potential.id_vk_user'), nullable=False)

    def __str__(self):
        return f'id_fаvоrite_user: {self.id_fovarite_user}, id_vk_user: {self.id_vk_user}'


class Black_list(Base):
    """Отвергнутые пользователи."""
    __tablename__ = 'black_list'
    __table_args__ = {'schema': 'pretenders'}
    id_black_list = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    id_vk_user = sq.Column(sq.Integer, sq.ForeignKey('pretenders.users_potential.id_vk_user'), nullable=False)

    def __str__(self):
        return f'id_black_list: {self.id_black_list}, id_vk_user: {self.id_vk_user}'
