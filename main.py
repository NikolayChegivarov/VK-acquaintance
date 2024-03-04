import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import TOKEN, GROUP_ID, user_token
from user_info import get_user_info, search_users_info, get_top_three_photos, get_next_pipl, get_city_id_by_name, age_range
from start_button import Buttons
from write_message import write_message
from bd import *
from pprint import pprint as pp
# from vk_api import VkUpload

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

# Для отправки изображений на сервер vk.
# upload = VkUpload(vk_session)

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

        pp(event)

        # Определяем id пользователя. peer_id так же
        # нужен в некоторых случаях где не подходит from_id.
        peer_id = event.object.get('peer_id')
        sender = event.object.get('from_id')
        user_info = vk_user.users.get(user_ids=sender,
                                      fields='first_name,last_name')  # Запрашиваем информацию о пользователе
        user_name = f"{user_info[0]['first_name']} {user_info[0]['last_name']}"  # Формируем полное имя пользователя
        print(f"Имя пользователя: {user_name}")

        # Получаем текст сообщения
        message_text = event.object.text
        print(f'сообщение: {message_text}')

        # Вложения.
        # attachments = []
        # upload_image = upload.photo_messages(photos=image)[0]
        # attachments.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))
        # Проверяем, есть ли уже сохраненные критерии для этого пользователя.

        print(f"Перед проверкой: user_states = {user_states}")
        if sender in user_states and 'criteria' in user_states[sender]:
            criteria = user_states[sender]['criteria']
            print(f'актуальные критерии {criteria}')
        else:
            # Получаем критерии, если они не были сохранены.
            criteria = get_user_info(vk_user, sender, vk_session, peer_id)
            user_states[sender] = {'criteria': criteria}
            print(f'Новые критерии {user_states}')

        status = user_states.get(sender, {}).get('status', None)


        # ЕСЛИ В КРИТЕРИЯХ НЕ ХВАТАЕТ ГОРОДА ИЛИ ДАТЫ РОЖДЕНИЯ.

        # Если есть диапазон нажимаем старт
        if status == 'criteria_with_range':
            user_states[sender]['status'] = 'START'

        # Обработка сообщения как ответ на запрос о городе
        if status == 'waiting_for_city':
            city_name = message_text
            city_identifier = get_city_id_by_name(city_name, vk_user)
            criteria['city'] = city_identifier
            del(user_states[sender]['status'])
            print(f"С городом {user_states}")

        # Обработка сообщения как ответ на запрос о дате рождения
        elif status == 'waiting_for_date':
            print('меняет дату')
            date_of_birth = message_text
            criteria['age'] = date_of_birth
            del(user_states[sender]['status'])
            print(f'С датой {user_states[sender]}')


        # ПРОВЕРКА НА ОТСУТСТВИЕ ГОРОДА ИЛИ ДАТЫ РОЖДЕНИЯ.
        # Если статус отсутствует
        if 'status' not in user_states.get(sender, {}):
            if criteria.get('city') == 'Город неуказан':
                write_message(vk_session, peer_id, 'Напишите город в котором хотите осуществить поиск.')
                user_states[sender]['status'] = 'waiting_for_city'
            elif criteria.get('age') == 'Возраст неуказан':
                write_message(vk_session, peer_id, 'Введите вашу дату рождения (формат: ДД.ММ.ГГГГ).')
                user_states[sender]['status'] = 'waiting_for_date'
            else:
                user_states.setdefault(sender, {})
                user_states[sender]['status'] = 'criteria_completed'
                print(f'Критерии укомплектованы: {user_states}')


        # УСТАНАВЛИВАЕМ ДИАПАЗОН И СРАЗУ ОТПРАВЛЯЕМ КНОПКУ СТАРТ
        status = user_states.get(sender, {}).get('status', None)
        # Если criteria укомплектован добавляем диапазон.
        if status == 'criteria_completed':
            user_states[sender] = age_range(user_states[sender])
            criteria = user_states[sender]['criteria']
            print(f'С диапазоном {user_states}')
            print(f'criteria {criteria}')

            # Для предотвращения повторной отправки сообщения с кнопкой «СТАРТ» пользователю.
            if peer_id not in start_message_sent or not start_message_sent[peer_id]:
                # Отправляем кнопку старт с предложением пользователю нажать ее.
                buttons_instance.button_START(vk_session, peer_id)
                start_message_sent[peer_id] = True
            user_states[sender]['status'] = 'criteria_with_range'
            print(f'Последний {user_states}')


        # КНОПКИ:
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
                    write_message(vk_session, peer_id,
                                  f'{pipl[3]} из {len(list_of_potential)} претeндентов.\n{pipl[0]}. \nСылка на профиль: {pipl[1]}.',
                                  attachments=photos)
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
                write_message(vk_session, peer_id, f'{pipl[0]} сохранили в список избранных.', attachments=None, keyboard=None, upload_image=None)
                # Создаем следующего.
                next_pipl = get_next_pipl(pipl, list_of_potential)
                # Если следующий есть, то выводим следующего.
                if next_pipl is not None:
                    pipl = next_pipl
                    photos = get_top_three_photos(pipl[2], vk_user)
                    write_message(vk_session, peer_id,
                                  f'{pipl[3]} из {len(list_of_potential)} претeндентов.\n{pipl[0]}. \nСылка на профиль: {pipl[1]}.',
                                  attachments=photos)
                    buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)
                else:
                    # В списке больше нет людей. Что бы вывести список избранных нажмите 'list')
                    buttons_instance.button_LIST(vk_session, sender)

            elif message_text == 'NEXT':
                # Добавляем в чс
                add_black_list(session, pipl)

                # Создаем следующего.
                next_pipl = get_next_pipl(pipl, list_of_potential)
                # Если следующий есть, то выводим следующего.
                if next_pipl is not None:
                    pipl = next_pipl
                    photos = get_top_three_photos(pipl[2], vk_user)
                    write_message(vk_session, peer_id,
                                  f'{pipl[3]} из {len(list_of_potential)} претeндентов.\n{pipl[0]}. \nСылка на профиль: {pipl[1]}.',
                                  attachments=photos)
                    buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)
                else:
                    # В списке больше нет людей. Что бы вывести список избранных нажмите 'list')
                    buttons_instance.button_LIST(vk_session, sender)

            elif message_text == 'LIST':
                # Выводим список избранных.
                list_favorites = view_favorites_users(session, peer_id, id_bot_user_)
                print(f'Избранные: {list_favorites}')
                # Отправляем этот список пользователю.
                write_message(vk_session, peer_id, f'{list_favorites}', attachments=None, keyboard=None, upload_image=None)
                buttons_instance.button_LIST_rejected_START(vk_session, sender)
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

"""
<<class 'vk_api.bot_longpoll.VkBotMessageEvent'>({
'group_id': 224584658,
'type': 'message_new',
'event_id': 'e05536163494386d55fe90cc98ad359f120848b7',
'v': '5.199',
'object':
    {'message': {
            'date':1707663065,
            'from_id': 23659472,
            'id': 255,
            'out': 0,
            'version': 10000759,
            'attachments': [],
            'conversation_message_id': 221,
            'fwd_messages': [],
            'important': False,
            'is_hidden': False,
            'peer_id': 23659472,
            'random_id': 0,
            'text': 'олролр'},
            'client_info': {
                'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback', 'intent_subscribe', 'intent_unsubscribe'],
                'keyboard': True,
                'inline_keyboard': True,
                'carousel': True,
                'lang_id': 0}}})>
"""
