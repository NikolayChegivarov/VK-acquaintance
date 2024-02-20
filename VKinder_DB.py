import os
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
load_dotenv()

Base = declarative_base()
class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, unique=True, nullable=False)
    def __str__(self):
        return f'id: {self.id}, user_id: {self.user_id}'

class Favorite_users(Base):
    __tablename__ = 'favorite_users'
    id = sq.Column(sq.Integer, primary_key=True)
    vk_user = sq.Column(sq.Integer, sq.ForeignKey(User.id), nullable=False)
    name = sq.Column(sq.String(length=100), nullable=False)
    link = sq.Column(sq.String(250), nullable=False)
    def __str__(self):
        return (f'id: {self.id}, user_id: {self.user_id}, name:{self.name}')

class Black_list(Base):
    __tablename__ = 'black_list'
    id = sq.Column(sq.Integer, primary_key=True)
    vk_user = sq.Column(sq.Integer, sq.ForeignKey(User.id), nullable=False)

def create_tables(engine):
    Base.metadata.drop_all(engine)

def drop_tables(engine):
    Base.metadata.create_all(engine)

def start_engine():
    secret_key = os.getenv("SECRET_KEY")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    DSN = f'postgresql://postgres:{secret_key}@{db_host}:{db_port}/VKinder_DB'
    engine = sq.create_engine(DSN)
    return engine

def add_favorite_user(pipl): #добавление избранных user в БД
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    name = pipl[0]
    link = pipl[1]
    vk_user = pipl[2]
    favorite_user_data = Favorite_users(
        name=name,
        link=link,
        vk_user=vk_user,
    )
    session.add(favorite_user_data)
    session.commit()
    session.close()

def view_favorites_users(user_id): #просмотр избранных user
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    results = session.query(Favorite_users).filter(Favorite_users.vk_user == user_id).all()
    result = []
    for res in results:
        result.append([res.name, res.link, res.user_id])
    return result

def add_black_list(pipl):
    engine = start_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    vk_user = pipl[2]
    black_list_user_data = Black_list(
        vk_user=vk_user)
    session.add(black_list_user_data)
    session.commit()
    session.close()