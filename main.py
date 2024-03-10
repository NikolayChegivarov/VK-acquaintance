from interaction import *
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import TOKEN, GROUP_ID
from bd import *
# Создаем экземпляр класса Bd.
Bd_instance = Bd(db_session)

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
        # Создаем экземпляр класса взаимодействия.
        interaction_instance = Interaction(event, user_states, vk_session, vk_user, peer_id, sender)
        # Получаем текст сообщения
        message_text = event.object.text
        # Если переменной нет, создаем ее.
        user_states = globals().setdefault('user_states', {})
        # Определяем статус
        status = user_states.get(sender, {}).get('status', None)
        # ЗАПРАШИВАЕМ ИНФОРМАЦИЮ О ПОЛЬЗОВАТЕЛЕ.
        if not user_states or not user_states.get(sender):
            interaction_instance.process_user_info_request()

        # СОЗДАЕМ КРИТЕРИИ.
        status = user_states.get(sender, {}).get('status', None)
        if status == 'Нужно получить критерии':
            interaction_instance.create_criteria()

        # ЗАПРАШИВАЕМ КРИТЕРИИ.
        status = user_states.get(sender, {}).get('status', None)
        status_2 = user_states.get(sender, {}).get('status2', None)
        if status == 'Запрос.':
            interaction_instance.process_criteria_creation(message_text)

        # ПРОВЕРКА НА ОТСУТСТВИЕ ГОРОДА ИЛИ ДАТЫ РОЖДЕНИЯ.
        status = user_states.get(sender, {}).get('status', None)
        if status == 'Нужно проверить критерии на комплектность.':
            interaction_instance.is_there_a_city_date()

        # УСТАНАВЛИВАЕМ ДИАПАЗОН И СРАЗУ ОТПРАВЛЯЕМ КНОПКУ СТАРТ.
        status = user_states.get(sender, {}).get('status', None)
        if status == 'Установить диапазон.':
            interaction_instance.set_range(buttons_instance)

        # START:
        status = user_states.get(sender, {}).get('status', None)
        if status == 'START':
            if message_text == 'START':
                interaction_instance.start()

        # searching
        elif status == 'searching':
            interaction_instance.searching(message_text)
