from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from write_message import write_message


class Buttons:
    def __init__(self, one_time=True):
        """Инициализируем class Buttons указываем одноразовый фактор по умолчанию"""
        self.one_time = one_time
        self.message_text = ""

    def set_message_text(self, message):
        """Для интеграции сообщения"""
        self.message_text = message

    def button_start(self, vk_session, user_id):
        """Кнопка со своим функционалом"""
        keyboard = VkKeyboard(one_time=self.one_time)
        keyboard.add_button('START', color=VkKeyboardColor.NEGATIVE)  # красная
        self.set_message_text("Если хочешь начать поиски, нажми 'старт'")
        self.send_message(vk_session, user_id, keyboard)

    def button_save_next_list(self, vk_session, user_id):
        """Кнопки со своим функционалом"""
        keyboard = VkKeyboard(one_time=self.one_time)
        keyboard.add_button('SAVE', color=VkKeyboardColor.POSITIVE)  # Зелёная
        keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)  # Синяя
        keyboard.add_button('LIST', color=VkKeyboardColor.SECONDARY)  # Белая
        text = ("Если хочешь добавить человека в список избранных нажми 'SAVE'. "
                "Если хочешь перейти к следующему человеку, нажми 'NEXT'. "
                "Если хочешь вывести список избранных нажми 'LIST'.")
        self.set_message_text(text)
        self.send_message(vk_session, user_id, keyboard)

    def button_list(self, vk_session, user_id):
        """Кнопка для просмотра избранных."""
        keyboard = VkKeyboard(one_time=self.one_time)
        keyboard.add_button('LIST', color=VkKeyboardColor.SECONDARY)  # Белая
        self.set_message_text("В списке больше нет людей. Что бы вывести список избранных нажмите 'list'")
        self.send_message(vk_session, user_id, keyboard)

    def button_list_rejected(self, vk_session, user_id):
        """Кнопка для просмотра отклоненных."""
        keyboard = VkKeyboard(one_time=self.one_time)
        keyboard.add_button('LIST_rejected', color=VkKeyboardColor.SECONDARY)  # Белая
        self.set_message_text("Это все пользователи VK которых вы добавили в избранное."
                              "При желании вывести список отклоненных пользователей, "
                              "вы можете воспользоваться кнопкой 'LIST_rejected'")
        self.send_message(vk_session, user_id, keyboard)

    def send_message(self, vk_session, user_id, keyboard):
        """Для интеграции метода сообщения в кнопку, с текстом в качестве аргумента"""
        attachments = []  # При необходимости заменю реальными вложениями.
        write_message(vk_session, user_id, self.message_text, attachments, keyboard)
