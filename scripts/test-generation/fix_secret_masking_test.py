import re

content = open("src/security/tests/test_secret_masking.py", "r", encoding="utf-8").read()

# Заменим строку
old_line = 'assert result["password"] == 0  # Числовые секреты заменяются на 0'
new_line = 'assert result["password"] == "****"  # Числа замаскированы как ****'

content = content.replace(old_line, new_line)

# Сохраним
with open("src/security/tests/test_secret_masking.py", "w", encoding="utf-8", newline="") as f:
    f.write(content)

print("Updated")
