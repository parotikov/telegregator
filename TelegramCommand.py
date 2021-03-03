import re

class TelegramCommand():
    """Обработчик входящих команд"""

    def __init__(self):
        """Инициализирует исходное сообщение"""
        self.command = None
        self.arg = None
        self.command_mask = '^\/([-a-zA-Z]+)\s?@?([-а-яА-Яa-zA-Z0-9@:.\/\\_\s]+)?'

    def parseMessage(self, message):
        """разбирает входящее сообщение на команду а аргумент"""
        m = re.search(self.command_mask, message)
        if m:
            self.arg = m.group(2)
            self.command = m.group(1)
        return self.command, self.arg