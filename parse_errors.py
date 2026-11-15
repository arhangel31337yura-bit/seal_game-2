try:
    with open("build_log.txt", "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
except FileNotFoundError:
    print("Лог-файл не найден!")
    exit(1)

# Ищем настоящие ошибки по всему логу
error_keywords = ["traceback", "command failed", "build failed", "syntaxerror", "exception", "fatal error", "killed", "memoryerror"]
ignore_keywords = ["-werror", "gcc ", "g++ ", "checking for"]

errors = []
for line in lines:
    line_lower = line.lower()
    if any(kw in line_lower for kw in error_keywords) and not any(ig in line_lower for ig in ignore_keywords):
        errors.append(line)

# Берем ровно последние 1000 строк для контекста
context = lines[-1000:] if len(lines) > 1000 else lines

with open("errors_only.txt", "w", encoding="utf-8") as f:
    f.write("=== НАЙДЕННЫЕ ОШИБКИ ===\n")
    if errors:
        f.writelines(errors)
    else:
        f.write("Строгих ошибок не найдено. Проверь последние строки лога ниже.\n")
        
    f.write("\n\n=== ПОСЛЕДНИЕ 1000 СТРОК ЛОГА (ДЛЯ КОНТЕКСТА) ===\n")
    f.writelines(context)
