import re

# Открываем лог, который создаст Buildozer
try:
    with open("build_log.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
except FileNotFoundError:
    print("Лог-файл не найден!")
    exit(1)

# Ищем строки с ошибками
error_keywords = ["error", "exception", "traceback", "failed"]
errors = [line for line in lines if any(kw in line.lower() for kw in error_keywords)]

# Берем последние 100 строк для контекста
context = lines[-100:] if len(lines) > 100 else lines

# Записываем все в чистый файл
with open("errors_only.txt", "w", encoding="utf-8") as f:
    f.write("=== НАЙДЕННЫЕ ОШИБКИ ===\n")
    if errors:
        f.writelines(errors)
    else:
        f.write("Строк со словами Error/Traceback не найдено.\n")
        
    f.write("\n\n=== ПОСЛЕДНИЕ 100 СТРОК ЛОГА (ДЛЯ КОНТЕКСТА) ===\n")
    f.writelines(context)

print("Ошибки успешно собраны в файл errors_only.txt!")
