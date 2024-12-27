import random
import string
from typing import Set

class PasswordGenerator:
    ENGLISH_CHARS = string.ascii_letters + string.digits
    SPECIAL_CHARS = "@#$%&*-+()!\"':;/?_–—[]{}><¡.,~`|•√Π÷×=^€¢£„"
    RUSSIAN_CHARS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    ASIAN_CHARS = ("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
                  "가나다라마바사아자차카타파하"
                  "你好谢谢再见早上好晚上好")

    def __init__(self):
        self.generated_passwords: Set[str] = set()

    def generate_password(self, length: int, password_type: str = "english") -> str:
        while True:
            if password_type == "english":
                chars = self.ENGLISH_CHARS + self.SPECIAL_CHARS
            elif password_type == "russian":
                chars = self.RUSSIAN_CHARS + string.digits + self.SPECIAL_CHARS
            elif password_type == "asian":
                chars = self.ASIAN_CHARS + string.digits + self.SPECIAL_CHARS
            else:
                chars = self.ENGLISH_CHARS + self.SPECIAL_CHARS

            password = ''.join(random.choice(chars) for _ in range(length))
            
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in self.SPECIAL_CHARS for c in password)
            
            if password not in self.generated_passwords and has_digit and has_special:
                self.generated_passwords.add(password)
                return password