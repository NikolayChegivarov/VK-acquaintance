from vk_api.utils import get_random_id
# from vk_api import VkUpload  Включить при необходимости выгрузить фото на сервер мк

def write_message(vk_session, peer_id, message, attachments=None, keyboard=None, upload_image=None):
    """Функция отправки сообщений пользователям."""

    print("Пытаемся отправить сообщение...")
    # Объедините предоставленные вложения с загруженным изображением, если таковое имеется.
    combined_attachments = attachments or []
    if upload_image:
        combined_attachments.extend(upload_image)

    # Преобразуйте список вложений в строку, разделенную запятыми.
    attachments_str = ','.join(combined_attachments)

    # Подготовьте клавиатуру JSON
    keyboard_json = keyboard.get_keyboard() if keyboard else None

    # Отправить сообщение с вложениями
    vk_session.method('messages.send', {
        'peer_id': peer_id,
        'message': message,
        'random_id': get_random_id(),
        'attachment': attachments_str,
        'keyboard': keyboard_json
    })
    print("Сообщение отправлено.")
