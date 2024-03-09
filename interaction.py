from user_info import *
from start_button import Buttons
from write_message import write_message
from bd import *

# Создаем экземпляр класса Buttons.
buttons_instance = Buttons(one_time=True)


class Interaction:

    def __init__(self, event):
        """Инициализируем class interaction."""
        self.event = event

    # ЗАПРАШИВАЕМ ИНФОРМАЦИЮ О ПОЛЬЗОВАТЕЛЕ.
    def process_user_info_request(self, vk_user, sender, user_states):
        print('ЗАПРАШИВАЕМ ИНФОРМАЦИЮ О ПОЛЬЗОВАТЕЛЕ')
        user_info = vk_user.users.get(user_ids=sender,
                                      fields='first_name,last_name')  # Запрашиваем информацию о пользователе
        user_name = f"{user_info[0]['first_name']} {user_info[0]['last_name']}"  # Формируем полное имя пользователя
        user_states[sender] = {'user_name': user_name}  # Добавляем имя в user_states
        add_bot_users(session, sender, user_name)  # Добавляем пользователя в б.д.
        user_states[sender]['status'] = 'Нужно получить кретерии'  # Меняем статус.
        print(f"данные о пользователе: {user_states}")
        return user_states

    # СОЗДАЕМ КРИТЕРИИ.
    def create_criteria(vk_session, vk_user, sender, user_states, peer_id):
        print('ПОЛУЧАЕМ КРЕТЕРИИ.')
        # Получаем критерии, если они не были сохранены.
        if sender in user_states and 'criteria' in user_states[sender]:
            criteria = user_states[sender]['criteria']
            print(f'актуальные критерии {criteria}')
        else:
            criteria = get_user_info(vk_user, sender, vk_session, peer_id)
            user_states[sender]['criteria'] = criteria
            print(f'Создали критерии {user_states}')
            user_states[sender]['status'] = 'Нужно проверить критерии на комплектность.'

    # ПОЛУЧЕНИЕ ГОРОДА ИЛИ ДАТЫ РОЖДЕНИЯ ИЗ ЗАПРОСА.
    def process_criteria_creation(self, vk_user, sender, user_states, message_text):
        status_2 = user_states.get(sender, {}).get('status2', None)
        if status_2 is None:
            print("'status2' is not set for the user.")
            return

        # Получаем город.
        if status_2 == 'Запросить город.':
            print('Запрашиваем город')
            user_state = user_states.get(sender, {})
            criteria = user_state.get('criteria', {})
            city_name = message_text
            city_identifier = get_city_id_by_name(city_name, vk_user)
            criteria['city'] = city_identifier
            user_states[sender]['status'] = 'Нужно проверить критерии на комплектность.'
            del (user_states[sender]['status2'])
            print(f"С городом {user_states}")

        # Получаем дату.
        elif status_2 == 'Запросить дату.':
            print('Запрашиваем дату')
            user_state = user_states.get(sender, {})
            criteria = user_state.get('criteria', {})
            date_of_birth = message_text
            criteria['age'] = date_of_birth
            user_states[sender]['status'] = 'Нужно проверить критерии на комплектность.'
            del (user_states[sender]['status2'])
            print(f'С датой {user_states[sender]}')

    # ПРОВЕРКА НА ОТСУТСТВИЕ И ЗАПРОС ГОРОДА ИЛИ ДАТЫ РОЖДЕНИЯ.
    def is_there_a_city_date(self, vk_session, sender, user_states, peer_id):
        user_state = user_states.get(sender, {})
        criteria = user_state.get('criteria', {})
        if criteria.get('city') == 'Город неуказан':
            write_message(vk_session, peer_id, 'Напишите город в котором хотите осуществить поиск.')
            user_states[sender]['status'] = 'Запрос.'
            user_states[sender]['status2'] = 'Запросить город.'
        elif criteria.get('age') == 'Возраст неуказан':
            write_message(vk_session, peer_id, 'Введите вашу дату рождения (формат: ДД.ММ.ГГГГ).')
            user_states[sender]['status'] = 'Запрос.'
            user_states[sender]['status2'] = 'Запросить дату.'
        else:
            user_states.setdefault(sender, {})
            user_states[sender]['status'] = 'Установить диапазон.'
            print(f'Критерии укомплектованы: {user_states}')

    # УСТАНАВЛИВАЕМ ДИАПАЗОН И СРАЗУ ОТПРАВЛЯЕМ КНОПКУ СТАРТ.
    def set_range(self, vk_session, peer_id, user_states, sender, buttons_instance):
        user_states[sender] = age_range(user_states[sender])
        criteria = user_states[sender]['criteria']
        print(f'С диапазоном {user_states}')
        print(f'criteria {criteria}')
        buttons_instance.button_start(vk_session, peer_id)
        user_states[sender]['status'] = 'START'
        print(f'Проверочный: {user_states}')

    # START:
    def start(self, user_states, sender, vk_user, vk_session, peer_id):
        print("кнопка старт нажата")
        # Осуществляем поиск потенциальных партнеров для пользователя.
        criteria = user_states[sender]['criteria']
        # Выводим список потенциальных.
        list_of_potential = search_users_info(criteria, search_count=1000)
        # Добавляем список потенциальных в user_states
        user_states[sender]['list_of_potential'] = list_of_potential
        # Записываем всех пользователей vk выбранных по критериям.
        add_all(session, list_of_potential, sender)
        # Отправляем информацию о первом кандидате пользователю.
        if list_of_potential:
            pipl = list_of_potential[0]
            photos = get_top_three_photos(pipl[2], vk_user)
            message = (
                f'{pipl[3]} из {len(list_of_potential)} претендентов.\n'
                f'{pipl[0]}. \n'
                f'Ссылка на профиль: {pipl[1]}.'
            )
            write_message(vk_session, peer_id, message, attachments=photos)
            print('Первый пошел.')
            # Отправляем клавиатуру "SAVE", "NEXT" и "LIST".
            buttons_instance.button_save_next_list(vk_session, sender)
            user_states[sender]['status'] = 'searching'
            return user_states

    def searching(self, sender, message_text, user_states, vk_session, peer_id, vk_user, user_id):
        id_bot_user_ = id_bot_user(sender)
        list_of_potential = user_states[sender]['list_of_potential']
        pipl = list_of_potential[0]
        if message_text == 'SAVE':
            # Сохраняем в избранное.
            add_favorite_user(session, pipl)
            # Сообщаем пользователю.
            message = f'{pipl[0]} сохранили в список избранных.'
            write_message(vk_session, peer_id, message, attachments=None, keyboard=None, upload_image=None)
            # Создаем следующего.
            next_pipl = get_next_pipl(pipl, list_of_potential)
            # Если следующий есть, то выводим следующего.
            if next_pipl is not None:
                pipl = next_pipl
                photos = get_top_three_photos(pipl[2], vk_user)
                message = (f'{pipl[3]} из {len(list_of_potential)} претендентов.'
                           f'\n{pipl[0]}. \nСсылка на профиль: {pipl[1]}.')
                write_message(vk_session, peer_id, message, attachments=photos)
                buttons_instance.button_save_next_list(vk_session, user_id)
                # Обновляем user_states с новым значением pipl.
                user_states[sender]['list_of_potential'] = list_of_potential[list_of_potential.index(pipl):]
            else:
                # В списке больше нет людей. Что бы вывести список избранных нажмите 'list'.
                buttons_instance.button_list(vk_session, user_id)
            pass

        elif message_text == 'NEXT':
            # Добавляем в чс.
            add_black_list(session, pipl)
            # Создаем следующего.
            next_pipl = get_next_pipl(pipl, list_of_potential)
            # Если следующий есть, то выводим следующего.
            if next_pipl is not None:
                pipl = next_pipl  # Обновляем локальную переменную pipl.
                photos = get_top_three_photos(pipl[2], vk_user)
                message = (f'{pipl[3]} из {len(list_of_potential)} претендентов.'
                           f'\n{pipl[0]}. \nСсылка на профиль: {pipl[1]}.')
                write_message(vk_session, peer_id, message, attachments=photos)
                buttons_instance.button_save_next_list(vk_session, user_id)
                # Обновляем user_states с новым значением pipl.
                user_states[sender]['list_of_potential'] = list_of_potential[list_of_potential.index(pipl):]
            else:
                # В списке больше нет людей. Что бы вывести список избранных нажмите 'list'.
                buttons_instance.button_list(vk_session, user_id)
            pass

        elif message_text == 'LIST':
            # Выводим список избранных.
            list_favorites = view_favorites_users(session, peer_id, id_bot_user_)
            print(f'Избранные: {list_favorites}')
            # Отправляем этот список пользователю.
            message = f'{list_favorites}'
            write_message(vk_session, peer_id, message, attachments=None, keyboard=None, upload_image=None)
            buttons_instance.button_list_rejected(vk_session, user_id)
            pass

        elif message_text == 'LIST_rejected':
            # Выводим список отклоненных.
            list_rejected = view_rejected_users(session, peer_id, id_bot_user_)
            print(f'Отклоненные: {list_rejected}')
            write_message(vk_session, peer_id, f'{list_rejected}', attachments=None, keyboard=None,
                          upload_image=None)
            pass
        else:
            print('Цикл пройден.')
