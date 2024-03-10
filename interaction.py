from user_info import *
from start_button import Buttons
from write_message import write_message
from bd import *

# Создаем экземпляр класса Buttons.
buttons_instance = Buttons(one_time=True)
# Создаем экземпляр класса Bd.
Bd_instance = Bd(db_session)

Bd_instance.test_connection()
# Создание схемы и таблицы.
Bd_instance.create_schema('pretenders')
Bd_instance.create_tables()


class Interaction:

    def __init__(self, event, user_states, vk_session, vk_user, peer_id, sender):
        """Инициализируем class interaction."""
        self.event = event
        self.user_states = user_states
        self.vk_session = vk_session
        self.vk_user = vk_user
        self.peer_id = peer_id
        self.sender = sender

    # ЗАПРАШИВАЕМ ИНФОРМАЦИЮ О ПОЛЬЗОВАТЕЛЕ.
    def process_user_info_request(self):
        print('ЗАПРАШИВАЕМ ИНФОРМАЦИЮ О ПОЛЬЗОВАТЕЛЕ')
        user_info = self.vk_user.users.get(user_ids=self.sender, fields='first_name,last_name')
        user_name = f"{user_info[0]['first_name']} {user_info[0]['last_name']}"
        self.user_states[self.sender] = {'user_name': user_name}
        Bd_instance.add_bot_users(self.sender, user_name)
        self.user_states[self.sender]['status'] = 'Нужно получить критерии'
        print(f"данные о пользователе: {self.user_states}")
        return self.user_states

    # СОЗДАЕМ КРИТЕРИИ.
    def create_criteria(self):
        print('ПОЛУЧАЕМ КРЕТЕРИИ.')
        if self.sender in self.user_states and 'criteria' in self.user_states[self.sender]:
            criteria = self.user_states[self.sender]['criteria']
            print(f'актуальные критерии {criteria}')
        else:
            criteria = get_user_info(self.vk_user, self.sender, self.vk_session, self.peer_id)
            self.user_states[self.sender]['criteria'] = criteria
            print(f'Создали критерии {self.user_states}')
            self.user_states[self.sender]['status'] = 'Нужно проверить критерии на комплектность.'

    # ЗАПРАШИВАЕМ КРИТЕРИИ.
    def process_criteria_creation(self, message_text):
        status_2 = self.user_states.get(self.sender, {}).get('status2', None)
        if status_2 is None:
            print("'status2' is not set for the user.")
            return

        # Получаем город.
        if status_2 == 'Запросить город.':
            print('Запрашиваем город')
            user_state = self.user_states.get(self.sender, {})
            criteria = user_state.get('criteria', {})
            city_name = message_text
            city_identifier = get_city_id_by_name(city_name, self.vk_user)
            criteria['city'] = city_identifier
            self.user_states[self.sender]['status'] = 'Нужно проверить критерии на комплектность.'
            del (self.user_states[self.sender]['status2'])
            print(f"С городом {self.user_states}")

        # Получаем дату.
        elif status_2 == 'Запросить дату.':
            print('Запрашиваем дату')
            user_state = self.user_states.get(self.sender, {})
            criteria = user_state.get('criteria', {})
            date_of_birth = message_text
            criteria['age'] = date_of_birth
            self.user_states[self.sender]['status'] = 'Нужно проверить критерии на комплектность.'
            del (self.user_states[self.sender]['status2'])
            print(f'С датой {self.user_states[self.sender]}')

    # ПРОВЕРКА НА ОТСУТСТВИЕ И ЗАПРОС ГОРОДА ИЛИ ДАТЫ РОЖДЕНИЯ.
    def is_there_a_city_date(self):
        user_state = self.user_states.get(self.sender, {})
        criteria = user_state.get('criteria', {})
        if criteria.get('city') == 'Город неуказан':
            write_message(self.vk_session, self.peer_id, 'Напишите город в котором хотите осуществить поиск.')
            self.user_states[self.sender]['status'] = 'Запрос.'
            self.user_states[self.sender]['status2'] = 'Запросить город.'
        elif criteria.get('age') == 'Возраст неуказан':
            write_message(self.vk_session, self.peer_id, 'Введите вашу дату рождения (формат: ДД.ММ.ГГГГ).')
            self.user_states[self.sender]['status'] = 'Запрос.'
            self.user_states[self.sender]['status2'] = 'Запросить дату.'
        else:
            self.user_states.setdefault(self.sender, {})
            self.user_states[self.sender]['status'] = 'Установить диапазон.'

    # УСТАНАВЛИВАЕМ ДИАПАЗОН И СРАЗУ ОТПРАВЛЯЕМ КНОПКУ СТАРТ.
    def set_range(self, buttons_instance):
        self.user_states[self.sender] = age_range(self.user_states[self.sender])
        buttons_instance.button_start(self.vk_session, self.peer_id)
        self.user_states[self.sender]['status'] = 'START'

    # START:
    def start(self):
        print("кнопка старт нажата")
        # Осуществляем поиск потенциальных партнеров для пользователя.
        criteria = self.user_states[self.sender]['criteria']
        # Выводим список потенциальных.
        list_of_potential = search_users_info(criteria, search_count=1000)
        # Добавляем список потенциальных в user_states
        self.user_states[self.sender]['list_of_potential'] = list_of_potential
        # Записываем всех пользователей vk выбранных по критериям.
        Bd_instance.add_all(list_of_potential, self.sender)
        # Отправляем информацию о первом кандидате пользователю.
        if list_of_potential:
            pipl = list_of_potential[0]
            photos = get_top_three_photos(pipl[2], self.vk_user)
            message = (
                f'{pipl[3]} из {len(list_of_potential)} претендентов.\n'
                f'{pipl[0]}. \n'
                f'Ссылка на профиль: {pipl[1]}.'
            )
            write_message(self.vk_session, self.peer_id, message, attachments=photos)
            print('Первый пошел.')
            # Отправляем клавиатуру "SAVE", "NEXT" и "LIST".
            buttons_instance.button_save_next_list(self.vk_session, self.sender)
            self.user_states[self.sender]['status'] = 'searching'
            return self.user_states

    def searching(self, message_text):
        list_of_potential = self.user_states[self.sender]['list_of_potential']
        pipl = list_of_potential[0]
        if message_text == 'SAVE':
            # Сохраняем в избранное.
            Bd_instance.add_favorite_user(pipl)
            # Сообщаем пользователю.
            message = f'{pipl[0]} сохранили в список избранных.'
            write_message(self.vk_session, self.peer_id, message, attachments=None, keyboard=None, upload_image=None)
            # Создаем следующего.
            next_pipl = get_next_pipl(pipl, list_of_potential)
            # Если следующий есть, то выводим следующего.
            if next_pipl is not None:
                pipl = next_pipl
                photos = get_top_three_photos(pipl[2], self.vk_user)
                message = (f'{pipl[3]} из {len(list_of_potential)} претендентов.'
                           f'\n{pipl[0]}. \nСсылка на профиль: {pipl[1]}.')
                write_message(self.vk_session, self.peer_id, message, attachments=photos)
                buttons_instance.button_save_next_list(self.vk_session, self.sender)
                # Обновляем user_states с новым значением pipl.
                self.user_states[self.sender]['list_of_potential'] = list_of_potential[list_of_potential.index(pipl):]
            else:
                # В списке больше нет людей. Что бы вывести список избранных нажмите 'list'.
                buttons_instance.button_list(self.vk_session, self.sender)
            pass

        elif message_text == 'NEXT':
            # Добавляем в чс.
            Bd_instance.add_black_list(pipl)
            # Создаем следующего.
            next_pipl = get_next_pipl(pipl, list_of_potential)
            # Если следующий есть, то выводим следующего.
            if next_pipl is not None:
                pipl = next_pipl  # Обновляем локальную переменную pipl.
                photos = get_top_three_photos(pipl[2], self.vk_user)
                message = (f'{pipl[3]} из {len(list_of_potential)} претендентов.'
                           f'\n{pipl[0]}. \nСсылка на профиль: {pipl[1]}.')
                write_message(self.vk_session, self.peer_id, message, attachments=photos)
                buttons_instance.button_save_next_list(self.vk_session, self.sender)
                # Обновляем user_states с новым значением pipl.
                self.user_states[self.sender]['list_of_potential'] = list_of_potential[list_of_potential.index(pipl):]
            else:
                # В списке больше нет людей. Что бы вывести список избранных нажмите 'list'.
                buttons_instance.button_list(self.vk_session, self.sender)
            pass

        elif message_text == 'LIST':
            # Выводим список избранных.
            list_favorites = Bd_instance.view_favorites_users(self.sender)
            print(f'Избранные: {list_favorites}')
            # Отправляем этот список пользователю.
            message = f'{list_favorites}'
            write_message(self.vk_session, self.peer_id, message, attachments=None, keyboard=None, upload_image=None)
            buttons_instance.button_list_rejected(self.vk_session, self.sender)
            pass

        elif message_text == 'LIST_rejected':
            # Выводим список отклоненных.
            list_rejected = Bd_instance.view_rejected_users(self.sender)
            print(f'Отклоненные: {list_rejected}')
            write_message(self.vk_session, self.peer_id, f'{list_rejected}', attachments=None, keyboard=None,
                          upload_image=None)
            pass
        else:
            print('Цикл пройден.')
