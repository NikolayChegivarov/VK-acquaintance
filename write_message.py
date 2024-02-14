from vk_api.utils import get_random_id
def write_message(vk_session, user_id, message, attachments=None, keyboard=None):
    """Функция для отправки сообщений пользователю."""
    # Обработка отсутствия вложений.
    attachments = attachments or []
    # Преобразовать список вложений в строку, разделенную запятыми.
    attachments_str = ','.join(map(str, attachments))
    # Обработка отсутствия клавиатуры в сообщении.
    if keyboard is not None:
        keyboard_json = keyboard.get_keyboard()
    else:
        keyboard_json = None
    # инициализируем отправку сообщений
    vk_session.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'random_id': get_random_id(),
        'attachments': attachments_str,
        'keyboard': keyboard_json
    })
