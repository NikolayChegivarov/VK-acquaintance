import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
#                   функция создания клавиатуры, цвета клавиатуры
from pprint import pprint as pp
from params import TOKEN, GROUP_ID, user_token
from user_info import get_user_info, search_users_info
from start_button import Buttons
from write_message import write_message

# Создаем сеанс с токеном бота.
vk_session = vk_api.VkApi(token=TOKEN)
# Получаю экземпляр API
vk = vk_session.get_api()

# Создаем сеанс с токеном пользователя.
vk_user_session = vk_api.VkApi(token=user_token)
# Получаю экземпляр API
vk_user = vk_user_session.get_api()

# Инициализируем длинный опрос бота с идентификатором нашей группы.
longpoll = VkBotLongPoll(vk_session, wait=25, group_id=GROUP_ID)
# Для отправки изображений
upload = VkUpload(vk_session)
# Задаем путь к изображению
image = 'C:/Users/1/Pictures/z3qBD0NOO-8.jpg'
# создаем экземпляр класса Buttons
buttons_instance = Buttons(one_time=True)

# Создаем цикл для постоянного прослушивания чата.
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        # вывожу всю информацию которая есть в событии, для дальнейшего анализа.
        # pp(event)
        # Получаем текст сообщения
        message_text = event.object.text
        # Получаем id отправителя
        sender = event.object.get('from_id')
        # вложения
        # attachments = []
        # upload_image = upload.photo_messages(photos=image)[0]
        # attachments.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))
        # устанавливаем критерии поиска исходя из критериев пользователя

        criteria = get_user_info(sender, vk_user)

        # ОБРАБОТКА СОБЫТИЙ.
        # Отправляем кнопку старт.
        buttons_instance.button_START(vk_session, sender)
        if message_text == 'START':
            # Осуществляем поиск
            list_of_potential = search_users_info(criteria, search_count=1000)
            print(len(list_of_potential))
            pp(list_of_potential)
            # 2 У тех людей, которые подошли под критерии поиска, получить три самые популярные фотографии в профиле.
            # Популярность определяется по количеству лайков.
            # ДОБАВЛЯЕМ ВСЕ НАЙДЕННОЕ В БАЗЫ ДАННЫХ - имя и фамилия, - ссылка на профиль,- три фотографии
            # 3 Выводить в чат с ботом информацию о пользователе в формате:
            # - имя и фамилия,
            # - ссылка на профиль,
            # - три фотографии в виде attachment(https://dev.vk.com/method/messages.send).
            # Должна быть возможность перейти к следующему человеку с помощью команды или кнопки.
            # ИЛИ сохранить пользователя в список избранных.
            buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)
        elif message_text == 'SAVE':
            # Сохранить ID пользователя в список избранных.
            buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)
            pass
        elif message_text == 'NEXT':
            # Перейти к следующему ИЛИ ВЫВЕСТИ СООБЩЕНИЕ ЧТО ПРИТЕНДЕНТЫ ЗАКОНЧИЛИСЬ.
            buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)
            pass
        elif message_text == 'LIST':
            pass
            # ВЫВЕСТИ СПИСОК СОХРАНЕННЫХ
            # # Если в списке что то есть:
            #     # выводит список
            #     write_message(vk_session, sender, 'Если захочешь еще воспользоваться ботом, напиши мне.')
            # # Если список пуст
            #     # Убираем клавиатуру.
            #     write_message(vk_session, sender, 'Список еще пуст.')
            #     buttons_instance.button_SAVE_NEXT_LIST(vk_session, sender)
            #     pass
        else:
            print('Что то пошло не так.')

# """
# <<class 'vk_api.bot_longpoll.VkBotMessageEvent'>({
# 'group_id': 224584658,
# 'type': 'message_new',
# 'event_id': 'e05536163494386d55fe90cc98ad359f120848b7',
# 'v': '5.199',
# 'object':
#     {'message': {
#             'date':1707663065,
#             'from_id': 23659472,
#             'id': 255,
#             'out': 0,
#             'version': 10000759,
#             'attachments': [],
#             'conversation_message_id': 221,
#             'fwd_messages': [],
#             'important': False,
#             'is_hidden': False,
#             'peer_id': 23659472,
#             'random_id': 0,
#             'text': 'олролр'},
#             'client_info': {
#                 'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback', 'intent_subscribe', 'intent_unsubscribe'],
#                 'keyboard': True,
#                 'inline_keyboard': True,
#                 'carousel': True,
#                 'lang_id': 0}}})>
# """
