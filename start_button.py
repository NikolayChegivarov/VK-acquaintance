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

    def button_START(self, vk_session, user_id):
        """Кнопка со своим функционалом"""
        keyboard = VkKeyboard(one_time=self.one_time)
        keyboard.add_button('START', color=VkKeyboardColor.NEGATIVE)  # красная
        self.set_message_text("Если хочешь начать поиски, нажми 'старт'")
        self.send_message(vk_session, user_id, keyboard)

    def button_SAVE_NEXT_LIST(self, vk_session, user_id):
        """Кнопки со своим функционалом"""
        keyboard = VkKeyboard(one_time=self.one_time)
        keyboard.add_button('SAVE', color=VkKeyboardColor.POSITIVE)  # Зелёная
        keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)  # Синяя
        keyboard.add_button('LIST', color=VkKeyboardColor.SECONDARY)  # Белая
        self.set_message_text("Если хочешь добавить человека в список избранных нажми 'SAVE'. Если хочешь перейти к следующему человеку, нажми 'NEXT'.")
        self.send_message(vk_session, user_id, keyboard)

    def send_message(self, vk_session, user_id, keyboard):
        """Для интеграции метода сообщения в кнопку, с текстом в качестве аргумента"""
        attachments = []  # При необходимости заменю реальными вложениями.
        write_message(vk_session, user_id, self.message_text, attachments, keyboard)
