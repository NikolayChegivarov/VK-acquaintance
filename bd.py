from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import *
from config import user, password, name_database

Base = declarative_base()

DSN = f"postgresql://{user}:{password}@localhost:5432/{name_database}"
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def test_connection():
    """Функция для тестирования подключения"""
    print('1')
    try:
        print('2')
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"Database version: {version}")
            return True
    except Exception as e:
        print('3')
        print(f"Connection test failed: {e}")
        return False
# test_connection()

def create_schema(engine, schema_name):
    """Создание схемы pretenders в бд"""
    with engine.connect() as connection:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
create_schema(engine, 'pretenders')

def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
create_tables(engine)

def add_favorite_user(pipl):
    session = Session()
    try:
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
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

def view_favorites_users(user_id):
    session = Session()
    results = session.query(Favorite_users).filter(Favorite_users.vk_user == user_id).all()
    result = []
    for res in results:
        result.append([res.name, res.link, res.vk_user])
    session.close()
    return result

def add_black_list(pipl):
    session = Session()
    try:
        vk_user = pipl[2]
        black_list_user_data = Black_list(
            vk_user=vk_user)
        session.add(black_list_user_data)
        session.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

session.commit()
session.close()
