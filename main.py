from interaction import *
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import TOKEN, GROUP_ID

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
        # Создаем экземпляр класса взаимодействия.
        interaction_instance = Interaction(event)
        # Идентифицируем пользователя.
        sender = event.object.get('from_id')
        peer_id = event.object.get('peer_id')
        # Получаем текст сообщения
        message_text = event.object.text
        # Если переменной нет, создаем ее.
        user_states = globals().setdefault('user_states', {})
        # Определяем статус
        status = user_states.get(sender, {}).get('status', None)
        # ЗАПРАШИВАЕМ ИНФОРМАЦИЮ О ПОЛЬЗОВАТЕЛЕ.
        if not user_states or not user_states.get(sender):
            interaction_instance.process_user_info_request(vk_user, sender, user_states)

        # СОЗДАЕМ КРИТЕРИИ.
        status = user_states.get(sender, {}).get('status', None)
        if status == 'Нужно получить кретерии':
            interaction_instance.create_criteria(vk_user, sender, user_states, peer_id)

        # ЗАПРАШИВАЕМ КРИТЕРИИ.
        status = user_states.get(sender, {}).get('status', None)
        status_2 = user_states.get(sender, {}).get('status2', None)
        if status == 'Запрос.':
            interaction_instance.process_criteria_creation(vk_user, sender, user_states, message_text)

        # ПРОВЕРКА НА ОТСУТСТВИЕ ГОРОДА ИЛИ ДАТЫ РОЖДЕНИЯ.
        status = user_states.get(sender, {}).get('status', None)
        if status == 'Нужно проверить критерии на комплектность.':
            interaction_instance.is_there_a_city_date(vk_session, sender, user_states, peer_id)

        # УСТАНАВЛИВАЕМ ДИАПАЗОН И СРАЗУ ОТПРАВЛЯЕМ КНОПКУ СТАРТ.
        status = user_states.get(sender, {}).get('status', None)
        if status == 'Установить диапазон.':
            interaction_instance.set_range(vk_session, peer_id, user_states, sender, buttons_instance)

        # START:
        status = user_states.get(sender, {}).get('status', None)
        if status == 'START':
            if message_text == 'START':
                interaction_instance.start(user_states, sender, vk_user, vk_session, peer_id)

        # searching
        elif status == 'searching':
            interaction_instance.searching(sender, message_text, user_states, vk_session, peer_id, vk_user, sender)
