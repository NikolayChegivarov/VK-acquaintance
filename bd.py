from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import *
from config import user, password, name_database

DSN = f"postgresql://{user}:{password}@localhost:5432/{name_database}"
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()

# Журнал sqlalchemy для пошагового просмотра и выявления проблем
# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def test_connection(session):
    """Функция для тестирования подключения."""
    try:
        with session.bind.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"Версия базы данных: {version}")
            return True
    except Exception as e:
        print(f"Проверка соединения не удалась: {e}")
        return False
test_connection(session)

def create_schema(session, schema_name):
    """Создание схемы pretenders в бд."""
    try:
        with session.begin():
            session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            session.commit()
            print('Создается схема.')
    except Exception as e:
        print(f"Ошибка создания схемы: {e}")
    finally:
        session.close()

def create_tables(session):
    """Создание всех таблиц."""
    try:
        # Устанавливаю путь поиска для схемы 'pretenders'.
        session.execute(text("SET search_path TO pretenders;"))
        # reflect подтягивает все из схемы, таким образом удалиться всё,
        # а не только то что есть в метаданных.
        Base.metadata.reflect(bind=engine)
        Base.metadata.drop_all(bind=session.bind)
        Base.metadata.create_all(bind=session.bind)
        session.commit()
        print('Не стираем таблицы если есть, создаем новые.')
    except Exception as e:
        print(f"Ошибка создания таблиц: {e}")
        raise
    finally:
        session.close()

# Создание схемы и таблицы.
create_schema(session, 'pretenders')
create_tables(session)

from sqlalchemy.sql import exists

def add_bot_users(session, sender, user_name):
    """Функция добавляет пользователя бота в таблицу bot_users."""
    # Проверяем, существует ли уже такой пользователь
    user_exists = session.query(exists().where(Bot_users.id_vk_user == sender)).scalar()

    if not user_exists:
        try:
            bot_users_data = Bot_users(
                id_vk_user=sender,
                user_name=user_name
            )
            session.add(bot_users_data)
            session.commit()
            print('Пользователь бота добавлен в базу.')
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            session.rollback()
        finally:
            session.close()
    else:
        print('Пользователь уже существует в базе.')



def id_bot_user(id_vk_user):
    """Функция для получения id пользователя из таблицы пользователей.
    Используется в функции add_all"""
    bot_user = session.query(Bot_users).filter(Bot_users.id_vk_user == id_vk_user).first()
    if bot_user:
        return bot_user.id_bot_user
    else:
        print(f"Пользователь бота с id_vk_user={id_vk_user} не найден.")
        return None

def add_all(session, list_of_potential, id_vk_user):
    """Функция добавляет всех претендентов."""
    print('Всех на карандашь.')
    for pipl in list_of_potential:
        try:
            vk_id = pipl[2]
            name = pipl[0]
            link = pipl[1]

            id_bot_user_ = id_bot_user(id_vk_user)

            favorite_user_data = Users_potential(
                id_bot_user=id_bot_user_,
                id_vk_user=vk_id,
                user_name=name,
                link=link
            )
            session.add(favorite_user_data)
            # print(f"Добавлен пользователь {name} с id_vk_user={vk_id}.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            session.rollback()
        finally:
            session.commit()
            session.close()

def add_favorite_user(session, pipl):
    """Функция добавляет избранных."""
    try:
        vk_id = pipl[2]
        favorite_user_data = Favorite_users(
            id_vk_user=vk_id
        )
        session.add(favorite_user_data)
        print(f'Добавили {vk_id} в избранное.')
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        session.rollback()
    finally:
        session.commit()
        session.close()

def add_black_list(session, pipl):
    """Добавление в черный список."""
    try:
        vk_user = pipl[2]
        black_list_user_data = Black_list(
            id_vk_user=vk_user)
        session.add(black_list_user_data)
        print(f'Добавили {pipl[0]} в чс.')
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        session.rollback()
    finally:
        session.commit()
        session.close()

def view_favorites_users(session, user_id, id_bot_user):
    """Просмотр избранных пользователей."""
    print('Попытка список.')
    results = session.query(Users_potential.user_name, Users_potential.link).\
        join(Bot_users, Bot_users.id_bot_user == Users_potential.id_bot_user).\
        join(Favorite_users, Favorite_users.id_vk_user == Users_potential.id_vk_user).\
        filter(Bot_users.id_bot_user == id_bot_user).\
        all()
    print(f'результат фовариты {results}')
    result = []
    for user_name, link in results:
        result.append([user_name, link])
    if result:
        formatted_result = '\n'.join(f"{user_name} - {link}" for user_name, link in result)
        session.commit()
        session.close()
        return f"Ваши избранные:\n{formatted_result}"
    else:
        session.commit()
        session.close()
        return "Ваш список избранных пуст."

def view_rejected_users(session, user_id, id_bot_user):
    """Просмотр отклоненных пользователей."""
    print('Попытка список.')
    results = session.query(Users_potential.user_name, Users_potential.link).\
        join(Bot_users, Bot_users.id_bot_user == Users_potential.id_bot_user).\
        join(Black_list, Black_list.id_vk_user == Users_potential.id_vk_user).\
        filter(Bot_users.id_bot_user == id_bot_user).\
        all()
    print(f'результат отклоненных {results}')
    result = []
    for user_name, link in results:
        result.append([user_name, link])
    if result:
        formatted_result = '\n'.join(f"{user_name} - {link}" for user_name, link in result)
        session.commit()
        session.close()
        return f"Ваш список отклоненных пользователей:\n{formatted_result}"
    else:
        session.commit()
        session.close()
        return "Ваш список отклоненных пуст."

