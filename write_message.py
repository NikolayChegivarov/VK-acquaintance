# from vk_api.utils import get_random_id
# from vk_api import VkUpload  # отвечает за загрузку файлов на сервер вк
#
# from vk_api.utils import get_random_id
# from vk_api import VkUpload
#
# def write_message(vk_session, user_id, message, attachments=None, keyboard=None):
#     """Функция для отправки сообщений пользователю."""
#     # Обработка отсутствия вложений.
#     combined_attachments = attachments or []
#
#     # Преобразовать список вложений в строку, разделенную запятыми.
#     attachments_str = ','.join(combined_attachments)
#
#     # Обработка отсутствия клавиатуры в сообщении.
#     if keyboard is not None:
#         keyboard_json = keyboard.get_keyboard()
#     else:
#         keyboard_json = None
#
#     # инициализируем отправку сообщений
#     vk_session.method('messages.send', {
#         'user_id': user_id,
#         'message': message,
#         'random_id': get_random_id(),
#         'attachments': attachments_str,
#         'keyboard': keyboard_json
#     })

from vk_api.utils import get_random_id
from vk_api import VkUpload

# def write_message(vk_session, peer_id, message, attachments=None, keyboard=None, upload_image=None):
#     """Функция для отправки сообщений пользователю."""
#     # Обработка отсутствия вложений.
#     combined_attachments = attachments or []
#
#     # Если для загрузки было передано изображение, выполните загрузку
#     if upload_image:
#         upload = VkUpload(vk_session)
#         uploaded_image = upload.photo_messages(photos=upload_image)[0]
#         # Correctly format the attachment string
#         combined_attachments.append('photo{}_{}'.format(uploaded_image['owner_id'], uploaded_image['id']))
#
#     # Преобразовать список вложений в строку, разделенную запятыми.
#     attachments_str = ','.join(combined_attachments)
#
#     # Обработка отсутствия клавиатуры в сообщении.
#     if keyboard is not None:
#         keyboard_json = keyboard.get_keyboard()
#     else:
#         keyboard_json = None
#
#     # инициализируем отправку сообщений
#     vk_session.method('messages.send', {
#         'peer_id': peer_id,  # Используем peer_id вместо user_id
#         'message': message,
#         'random_id': get_random_id(),
#         'attachments': attachments_str,
#         'keyboard': keyboard_json
#     })

def write_message(vk_session, peer_id, message, attachments=None, keyboard=None, upload_image=None):
    """Function to send messages to users."""
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
