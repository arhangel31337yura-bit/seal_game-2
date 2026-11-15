import os

filename = "build_log.txt"

if not os.path.exists(filename):
    with open("errors_only.txt", "w", encoding="utf-8") as f:
        f.write("КРИТИЧЕСКАЯ ОШИБКА: Лог-файл build_log.txt не создан. Сборка упала ДО запуска Buildozer (проблема с зависимостями или кэшем).")
    exit(0)

try:
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
except Exception as e:
    with open("errors_only.txt", "w", encoding="utf-8") as f:
        f.write(f"Ошибка чтения лога: {e}")
    exit(0)

error_keywords = ["traceback", "command failed", "build failed", "syntaxerror", "exception", "fatal error", "killed", "memoryerror", "should have same version", "no such file"]
ignore_keywords = ["-werror", "gcc ", "g++ ", "checking for"]

errors = []
for line in lines:
    line_lower = line.lower()
    if any(kw in line_lower for kw in error_keywords) and not any(ig in line_lower for ig in ignore_keywords):
        errors.append(line)

context = lines[-1000:] if len(lines) > 1000 else lines

with open("errors_only.txt", "w", encoding="utf-8") as f:
    f.write("=== НАЙДЕННЫЕ ОШИБКИ ===\n")
    if errors:
        f.writelines(errors)
    else:
        f.write("Строгих ошибок не найдено. Проверь последние 1000 строк ниже.\n")
        
    f.write("\n\n=== ПОСЛЕДНИЕ 1000 СТРОК ЛОГА ===\n")
    f.writelines(context)
