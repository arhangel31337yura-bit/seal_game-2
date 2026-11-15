import re

try:
    with open("build_log.txt", "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
except FileNotFoundError:
    print("Лог-файл не найден!")
    exit(1)

# Ловим реальные ошибки И нехватку памяти
error_keywords = ["traceback", "command failed", "build failed", "syntaxerror", "exception", "fatal error", "killed", "memoryerror"]
# Игнорируем команды компиляции
ignore_keywords = ["-werror", "gcc ", "g++ ", "checking for"]

errors = []
for line in lines:
    line_lower = line.lower()
    if any(kw in line_lower for kw in error_keywords) and not any(ig in line_lower for ig in ignore_keywords):
        errors.append(line)

context = lines[-50:] if len(lines) > 50 else lines

with open("errors_only.txt", "w", encoding="utf-8") as f:
    f.write("=== НАСТОЯЩИЕ ОШИБКИ ===\n")
    if errors:
        f.writelines(errors)
    else:
        f.write("Строгих ошибок не найдено. Возможно, не хватило памяти (Killed).\n")
        
    f.write("\n\n=== ПОСЛЕДНИЕ 50 СТРОК ЛОГА (СМОТРИ ТУТ) ===\n")
    f.writelines(context)
