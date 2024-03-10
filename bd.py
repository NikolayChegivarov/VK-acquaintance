from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import *
from config import user, password, name_database
from sqlalchemy.sql import exists

DSN = f"postgresql://{user}:{password}@localhost:5432/{name_database}"
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
db_session = Session()

# Журнал sqlalchemy для пошагового просмотра и выявления проблем
# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class Bd:

    def __init__(self, db_session_):
        """Инициализируем class interaction."""
        self.db_session = db_session_

    def test_connection(self):
        """Функция для тестирования подключения."""
        try:
            with self.db_session.bind.connect() as connection:
                result = connection.execute(text("SELECT version();"))
                version = result.scalar()
                print(f"Версия базы данных: {version}")
                return True
        except Exception as e:
            print(f"Проверка соединения не удалась: {e}")
            return False

    def create_schema(self, schema_name):
        """Создание схемы pretenders в бд."""
        try:
            with self.db_session.begin():
                self.db_session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                self.db_session.commit()
                print('Создали схему.')
        except Exception as e:
            print(f"Ошибка создания схемы: {e}")
        finally:
            self.db_session.close()

    def create_tables(self):
        """Создание всех таблиц."""
        try:
            self.db_session.execute(text("SET search_path TO pretenders;"))
            Base.metadata.reflect(bind=engine)
            Base.metadata.drop_all(bind=self.db_session.bind)
            Base.metadata.create_all(bind=self.db_session.bind)
            self.db_session.commit()
            print('Стираем таблицы если есть, создаем новые.')
        except Exception as e:
            print(f"Ошибка создания таблиц: {e}")
            raise
        finally:
            self.db_session.close()

    def add_bot_users(self, sender, user_name):
        """Функция добавляет пользователя бота в таблицу bot_users.
        Используется в process_user_info_request"""
        user_exists = self.db_session.query(exists().where(BotUsers.id_vk_user == sender)).scalar()

        if not user_exists:
            try:
                bot_users_data = BotUsers(
                    id_vk_user=sender,
                    user_name=user_name
                )
                self.db_session.add(bot_users_data)
                self.db_session.commit()
                print('Пользователь бота добавлен в базу.')
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                self.db_session.rollback()
            finally:
                self.db_session.close()
        else:
            print('Пользователь уже существует в базе.')

    def id_bot_user(self, sender):
        """Функция для получения id пользователя из таблицы пользователей.
        Используется в методе add_all."""
        bot_user = self.db_session.query(BotUsers).filter(BotUsers.id_vk_user == sender).first()
        if bot_user:
            return bot_user.id_bot_user
        else:
            print(f"Пользователь бота с id_vk_user={sender} не найден.")
            return None

    def add_all(self, list_of_potential, sender):
        """Функция добавляет всех претендентов."""
        print('Всех на карандаш.')
        for pipl in list_of_potential:
            try:
                vk_id = pipl[2]
                name = pipl[0]
                link = pipl[1]
                id_bot_user = self.id_bot_user(sender)
                favorite_user_data = UsersPotential(
                    id_bot_user=id_bot_user,
                    id_vk_user=vk_id,
                    user_name=name,
                    link=link
                )
                self.db_session.add(favorite_user_data)
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                self.db_session.rollback()
            finally:
                self.db_session.commit()
                self.db_session.close()

    def add_favorite_user(self, pipl):
        """Функция добавляет избранных."""
        try:
            vk_id = pipl[2]
            favorite_user_data = FavoriteUsers(
                id_vk_user=vk_id
            )
            self.db_session.add(favorite_user_data)
            print(f'Добавили {vk_id} в избранное.')
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            self.db_session.rollback()
        finally:
            self.db_session.commit()
            self.db_session.close()

    def add_black_list(self, pipl):
        """Добавление в черный список."""
        try:
            vk_user = pipl[2]
            black_list_user_data = BlackList(
                id_vk_user=vk_user)
            self.db_session.add(black_list_user_data)
            print(f'Добавили {pipl[0]} в чс.')
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            self.db_session.rollback()
        finally:
            self.db_session.commit()
            self.db_session.close()

    def view_favorites_users(self, sender):
        """Просмотр избранных пользователей."""
        print('Попытка список.')
        id_bot_user = self.id_bot_user(sender)
        results = self.db_session.query(UsersPotential.user_name, UsersPotential.link). \
            join(BotUsers, BotUsers.id_bot_user == UsersPotential.id_bot_user). \
            join(FavoriteUsers, FavoriteUsers.id_vk_user == UsersPotential.id_vk_user). \
            filter(BotUsers.id_bot_user == id_bot_user). \
            all()
        result = []
        for user_name, link in results:
            result.append([user_name, link])
        if result:
            formatted_result = '\n'.join(f"{user_name} - {link}" for user_name, link in result)
            self.db_session.commit()
            self.db_session.close()
            return f"Ваши избранные:\n{formatted_result}"
        else:
            self.db_session.commit()
            self.db_session.close()
            return "Ваш список избранных пуст."

    def view_rejected_users(self, sender):
        """Просмотр отклоненных пользователей."""
        id_bot_user = self.id_bot_user(sender)
        results = self.db_session.query(UsersPotential.user_name, UsersPotential.link). \
            join(BotUsers, BotUsers.id_bot_user == UsersPotential.id_bot_user). \
            join(BlackList, BlackList.id_vk_user == UsersPotential.id_vk_user). \
            filter(BotUsers.id_bot_user == id_bot_user). \
            all()
        result = []
        for user_name, link in results:
            result.append([user_name, link])
        if result:
            formatted_result = '\n'.join(f"{user_name} - {link}" for user_name, link in result)
            self.db_session.commit()
            self.db_session.close()
            return f"Ваш список отклоненных пользователей:\n{formatted_result}"
        else:
            self.db_session.commit()
            self.db_session.close()
            return "Ваш список отклоненных пуст."
