from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import *
from config import user, password, name_database

DSN = f"postgresql://{user}:{password}@localhost:5432/{name_database}"
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()

# Журнал sqlalchemy.
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
        print('Стираем таблицы если есть, создаем новые.')
    except Exception as e:
        print(f"Ошибка создания таблиц: {e}")
        raise
    finally:
        session.close()

# Создание схемы и таблиц.
create_schema(session, 'pretenders')
create_tables(session)

def add_all(session, list_of_potential):
    """Функция добавляет всех претендентов."""
    print('Всех на карандашь.')
    for pipl in list_of_potential:
        try:
            name = pipl[0]
            link = pipl[1]
            vk_id = pipl[2]
            favorite_user_data = Users(
                name=name,
                link=link,
                vk_id=vk_id,
            )
            session.add(favorite_user_data)
            session.commit()
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            session.rollback()
        finally:
            session.close()

def add_favorite_user(session, pipl):
    """Функция добавляет избранных."""
    print(f'Добавили {pipl[0]} в избранное.')
    try:
        vk_id = pipl[2]
        favorite_user_data = Favorite_users(
            vk_id=vk_id
        )
        session.add(favorite_user_data)
        session.commit()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        session.rollback()
    finally:
        session.close()

def add_black_list(session, pipl):
    """Добавление в черный список."""
    print('Добавили pipl[0] в чс.')
    try:
        vk_user = pipl[2]
        black_list_user_data = Black_list(
            vk_user=vk_user)
        session.add(black_list_user_data)
        session.commit()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        session.rollback()
    finally:
        session.close()

def view_favorites_users(session, user_id):
    """Просмотр избранных пользователей."""
    print('Вывели список.')
    results = session.query(Favorite_users, Users).join(Users, Favorite_users.vk_id == Users.vk_id).filter(Users.user_id == user_id).all()
    print(results)
    result = []
    for res, user in results:
        result.append([user.name, user.link, user.vk_id])
    print(result)
    # Форматируем результат в строку
    if result:
        formatted_result = '\n'.join(f"{name} - {link}" for name, link, vk_id in result)
        session.commit()
        session.close()
        return f"Ваши избранные:\n{formatted_result}"
    else:
        session.commit()
        session.close()
        return "Ваш список избранных пуст."






