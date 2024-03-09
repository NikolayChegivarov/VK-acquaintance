# import vk_api
# from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
# from config import TOKEN, GROUP_ID
# from user_info import *
# from start_button import Buttons
# from write_message import write_message
# from bd import *
# from pprint import pprint as pp

# Создаем сеанс с токеном бота.
vk_session = vk_api.VkApi(token=TOKEN)
# Получаю экземпляр API.
vk = vk_session.get_api()

# Создаем сеанс с токеном пользователя.
vk_user_session = vk_api.VkApi(token=user_token)
# Получаю экземпляр API.
vk_user = vk_user_session.get_api()

# Инициализируем длинный опрос бота с идентификатором нашей группы.
longpoll = VkBotLongPoll(vk_session, wait=25, group_id=GROUP_ID)

# Создаем экземпляр класса Buttons.
buttons_instance = Buttons(one_time=True)

# Создаем словарь для отслеживания состояния пользователей
user_states = {}

# Создаем переменную для отслеживания отправки сообщения с кнопками "START"
start_message_sent = {}

pipl = None

# Прослушиваем все события с чата.
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:

        # Идентифицируем пользователя.
        sender = event.object.get('from_id')
        peer_id = event.object.get('peer_id')

        # Получаем текст сообщения
        message_text = event.object.text
        print(f'сообщение: {message_text}')

        # Если переменной нет, создаем ее.
        user_states = globals().setdefault('user_states', {})

        # Определяем статус
        status = user_states.get(sender, {}).get('status', None)

        print(f"ВХОДЯЩИЕ ДАННЫЕ: {user_states}")

        # ЗАПРАШИВАЕМ ИНФОРМАЦИЮ О ПОЛЬЗОВАТЕЛЕ.
        if not user_states or not user_states.get(sender):
            print('ЗАПРАШИВАЕМ ИНФОРМАЦИЮ О ПОЛЬЗОВАТЕЛЕ')
            user_info = vk_user.users.get(user_ids=sender,
                                          fields='first_name,last_name') # Запрашиваем информацию о пользователе
            user_name = f"{user_info[0]['first_name']} {user_info[0]['last_name']}" # Формируем полное имя пользователя
            user_states[sender] = {'user_name': user_name}
            add_bot_users(session, sender, user_name)
            user_states[sender]['status'] = 'Нужно получить кретерии'
            print(f"ДАННЫЕ О ПОЛЬЗОВАТЕЛЕ: {user_states}")

        # СОЗДАЕМ КРИТЕРИИ.
        status = user_states.get(sender, {}).get('status', None)
        if status == 'Нужно получить кретерии':
            print('Получаем критерии.')
            # Если User_id сохранен, сохраняем его # Получаем критерии, если они не были сохранены.
            if sender in user_states and 'criteria' in user_states[sender]:
                criteria = user_states[sender]['criteria']
                print(f'актуальные критерии {criteria}')
            else:
                criteria = get_user_info(vk_user, sender, vk_session, peer_id)
                user_states[sender]['criteria'] = criteria
                print(f'Создаем критерии {user_states}')
                user_states[sender]['status'] = 'Нужно проверить критерии на комплектность.'

        # ЗАПРАШИВАЕМ КРИТЕРИИ ЕСЛИ ОНИ ОТСУТСТВУЮТ.
        status = user_states.get(sender, {}).get('status', None)
        status_2 = user_states.get(sender, {}).get('status2', None)
        if status == 'Запрос.':
            # Запрашиваем город.
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

            # Запрашиваем дату.
            # status_ = user_states.get(sender, {}).get('status2', None)
            elif status_2 == 'Запросить дату.':
                print('Запрашиваем дату')
                user_state = user_states.get(sender, {})
                criteria = user_state.get('criteria', {})
                date_of_birth = message_text
                criteria['age'] = date_of_birth
                user_states[sender]['status'] = 'Нужно проверить критерии на комплектность.'
                del (user_states[sender]['status2'])
                print(f'С датой {user_states[sender]}')

        # ПРОВЕРКА НА ОТСУТСТВИЕ ГОРОДА ИЛИ ДАТЫ РОЖДЕНИЯ.
        status = user_states.get(sender, {}).get('status', None)
        if status == 'Нужно проверить критерии на комплектность.':
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
            print(f"Посмотреть второй статус: {user_states}")

        # УСТАНАВЛИВАЕМ ДИАПАЗОН И СРАЗУ ОТПРАВЛЯЕМ КНОПКУ СТАРТ.
        status = user_states.get(sender, {}).get('status', None)
        if status == 'Установить диапазон.':
            user_states[sender] = age_range(user_states[sender])
            criteria = user_states[sender]['criteria']
            print(f'С диапазоном {user_states}')
            print(f'criteria {criteria}')

            # Для предотвращения повторной отправки сообщения с кнопкой «СТАРТ» пользователю.
            if peer_id not in start_message_sent or not start_message_sent[peer_id]:
                # Отправляем кнопку старт с предложением пользователю нажать ее.
                buttons_instance.button_START(vk_session, peer_id)
                start_message_sent[peer_id] = True
            user_states[sender]['status'] = 'START'
            print(f'Проверочный: {user_states}')

        # КНОПКИ:
        status = user_states.get(sender, {}).get('status', None)
        if status == 'START':
            if message_text == 'START':
                print("кнопка старт нажата")

                # Осуществляем поиск потенциальных партнеров для пользователя.
                list_of_potential = search_users_info(criteria, search_count=1000)
                pp(len(list_of_potential))
                pp(list_of_potential)
                # Добавляем пользователя в таблицу пользователей.
                add_bot_users(session, sender, user_name)
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
                    buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)
                    user_states[sender]['status'] = 'searching'

        # если пользователь в статусе 'searching' запускаем этот цикл.
        elif status == 'searching':
            id_bot_user_ = id_bot_user(sender)
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
                    message = (f'{pipl[3]} из {len(list_of_potential)} претeндентов.'
                               f'\n{pipl[0]}. \nСсылка на профиль: {pipl[1]}.')
                    write_message(vk_session, peer_id, message, attachments=photos)
                    buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)
                else:
                    # В списке больше нет людей. Что бы вывести список избранных нажмите 'list'.
                    buttons_instance.button_LIST(vk_session, sender)

            elif message_text == 'NEXT':
                print(f'входящий{pipl}')
                # Добавляем в чс
                add_black_list(session, pipl)
                # Создаем следующего.
                next_pipl = get_next_pipl(pipl, list_of_potential)
                print(f'входящий{list_of_potential}')
                print(f'следующий{next_pipl}')
                # Если следующий есть, то выводим следующего.
                if next_pipl is not None:
                    pipl = next_pipl
                    photos = get_top_three_photos(pipl[2], vk_user)
                    message = (f'{pipl[3]} из {len(list_of_potential)} претeндентов.'
                               f'\n{pipl[0]}. \nСсылка на профиль: {pipl[1]}.')
                    write_message(vk_session, peer_id, message, attachments=photos)
                    buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)
                else:
                    # В списке больше нет людей. Что бы вывести список избранных нажмите 'list'.
                    buttons_instance.button_LIST(vk_session, sender)

            elif message_text == 'LIST':
                # Выводим список избранных.
                list_favorites = view_favorites_users(session, peer_id, id_bot_user_)
                print(f'Избранные: {list_favorites}')
                # Отправляем этот список пользователю.
                message = f'{list_favorites}'
                write_message(vk_session, peer_id, message, attachments=None, keyboard=None, upload_image=None)
                pass

            elif message_text == 'LIST_rejected':
                # Выводим список отклоненных.
                list_rejected = view_rejected_users(session, peer_id, id_bot_user_)
                print(f'Откланенные: {list_rejected}')
                write_message(vk_session, peer_id, f'{list_rejected}', attachments=None, keyboard=None,
                              upload_image=None)
                pass

            else:
                print('Цикл пройден.')
                continue
