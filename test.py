import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
#                   функция создания клавиатуры, цвета клавиатуры.
from pprint import pprint as pp
from config import TOKEN, GROUP_ID, user_token
from user_info import get_user_info, search_users_info, get_top_three_photos, get_next_pipl
from start_button import Buttons
from write_message import write_message
from bd import *

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

        # Определяем id пользователя. peer_id так же нужен в некоторых случаях где не подходит from_id.
        peer_id = event.object.get('peer_id')
        sender = event.object.get('from_id')

        # Вывожу всю информацию которая есть в событии, для дальнейшего анализа.
        # pp(event)

        # Получаем текст сообщения
        message_text = event.object.text
        print(message_text)

        # Вложения.
        # attachments = []
        # upload_image = upload.photo_messages(photos=image)[0]
        # attachments.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))

        # Устанавливаем критерии поиска исходя из критериев пользователя.
        criteria = get_user_info(sender, vk_user)

        # Для предотвращения повторной отправки сообщения с кнопкой «СТАРТ» пользователю.
        if peer_id not in start_message_sent or not start_message_sent[peer_id]:
            buttons_instance.button_START(vk_session, peer_id)
            start_message_sent[peer_id] = True
        user_states[peer_id] = 'searching'

        # ОБРАБОТКА СОБЫТИЙ:

        if message_text == 'START':
            print("кнопка старт нажата")

            # Осуществляем поиск потенциальных партнеров для пользователя.
            list_of_potential = search_users_info(criteria, search_count=1000)
            # pp(len(list_of_potential))
            # pp(list_of_potential)

            add_all(session, list_of_potential)

            # Отправляем информацию о первом кандидате.
            if list_of_potential:
                pipl = list_of_potential[0]

                photos = get_top_three_photos(pipl[2], vk_user)
                write_message(vk_session, peer_id,
                              f'{pipl[3]} из {len(list_of_potential)} претeндентов.\n{pipl[0]}. \nСылка на профиль: {pipl[1]}.',
                              attachments=photos)
                print('Первый пошел.')

                # Отправляем клавиатуру "SAVE", "NEXT" и "LIST".
                buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)

        # если пользователь в статусе 'searching' запускаем этот цикл.
        elif user_states.get(peer_id) == 'searching':
            if message_text == 'SAVE':
                # Сохраняем в избранное.
                add_favorite_user(session, pipl)
                # Сообщаем пользователю.
                write_message(vk_session, peer_id, f'{pipl[0]} сохранили в спимок избранных.', attachments=None, keyboard=None, upload_image=None)
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

                # ВЫВЕСТИ СПИСОК СОХРАНЕННЫХ
                # # Если в списке что то есть:
                #     # выводит список
                #     write_message(vk_session, sender, 'Если захочешь еще воспользоваться ботом, напиши мне.')
                # # Если список пуст
                #     # Убираем клавиатуру.
                #     write_message(vk_session, sender, 'Список еще пуст.')
                #     buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)
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
