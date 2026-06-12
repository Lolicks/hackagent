#!/bin/bash
# Jim AI Agent - Установщик

set -e

VERSION="2.0.0"
JIM_DIR="$HOME/jim-ai"
BIN_DIR="$HOME/.local/bin"
JIM_CMD="$BIN_DIR/jim"

# Цвета
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
CYAN='\033[96m'
BOLD='\033[1m'
END='\033[0m'

echo -e "${BOLD}${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                    JIM AI AGENT - УСТАНОВЩИК                              ║"
echo "║                         v$VERSION                                         ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo -e "${END}"

# 1. Создание директории
echo -e "\n${BLUE}📁 Создание директории Jim...${END}"
mkdir -p "$JIM_DIR"
mkdir -p "$BIN_DIR"
echo -e "${GREEN}✅ Директория создана: $JIM_DIR${END}"

# 2. Копирование файлов
echo -e "\n${BLUE}📄 Копирование файлов...${END}"

# Копируем jim.py
if [ -f "jim.py" ]; then
    cp jim.py "$JIM_DIR/"
else
    echo -e "${YELLOW}⚠️ jim.py не найден, создаю...${END}"
    # Здесь должен быть код jim.py, но предполагается что файл рядом
fi
chmod +x "$JIM_DIR/jim.py"

# 3. Создание .env
echo -e "\n${BLUE}🔑 Настройка API ключа...${END}"
if [ ! -f "$JIM_DIR/.env" ]; then
    echo -e "${YELLOW}Введите ваш OpenRouter API ключ:${END}"
    echo -n "> "
    read API_KEY
    echo "OPENROUTER_API_KEY=$API_KEY" > "$JIM_DIR/.env"
    echo -e "${GREEN}✅ API ключ сохранён в $JIM_DIR/.env${END}"
else
    echo -e "${GREEN}✅ .env уже существует${END}"
fi

# 4. Создание system_prompt.txt (если нет)
if [ ! -f "$JIM_DIR/system_prompt.txt" ]; then
    cat > "$JIM_DIR/system_prompt.txt" << 'EOF'
Ты - Jim, автономный ИИ-агент для пентеста Kali Linux.

## ТВОЙ АЛГОРИТМ:
1. Получи цель от пользователя
2. Выбери подходящие утилиты
3. Проанализируй вывод
4. Прими решение о следующих действиях
5. Выдай отчёт

Будь профессиональным и дружелюбным!
EOF
    echo -e "${GREEN}✅ Создан system_prompt.txt${END}"
fi

# 5. Создание глобальной команды
echo -e "\n${BLUE}🔗 Создание глобальной команды 'jim'...${END}"

cat > "$JIM_CMD" << EOF
#!/bin/bash
cd "$JIM_DIR"
python3 jim.py "\$@"
EOF

chmod +x "$JIM_CMD"
echo -e "${GREEN}✅ Команда создана: $JIM_CMD${END}"

# 6. Добавление в PATH
echo -e "\n${BLUE}📝 Проверка PATH...${END}"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "${YELLOW}⚠️ $BIN_DIR не в PATH. Добавьте строку в ~/.bashrc:${END}"
    echo -e "${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${END}"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo -e "${GREEN}✅ Добавлено в ~/.bashrc${END}"
fi

# 7. Установка Python зависимостей
echo -e "\n${BLUE}🐍 Установка Python зависимостей...${END}"
if command -v pip3 &> /dev/null; then
    pip3 install openai python-dotenv --quiet
    echo -e "${GREEN}✅ Зависимости установлены${END}"
else
    echo -e "${YELLOW}⚠️ pip3 не найден. Установите вручную: pip install openai python-dotenv${END}"
fi

# 8. Проверка утилит
echo -e "\n${BLUE}🛠️ Проверка системных утилит...${END}"
UTILS="nmap sqlmap gobuster nikto whatweb"
MISSING=""
for util in $UTILS; do
    if command -v $util &> /dev/null; then
        echo -e "${GREEN}✅ $util${END}"
    else
        echo -e "${RED}❌ $util не найден${END}"
        MISSING="$MISSING $util"
    fi
done

if [ -n "$MISSING" ]; then
    echo -e "\n${YELLOW}⚠️ Некоторые утилиты не установлены. Установите их:${END}"
    echo -e "${CYAN}sudo apt install$MISSING${END}"
fi

# 9. Итог
echo -e "\n${BOLD}${GREEN}═══════════════════════════════════════════════════════════════════════════${END}"
echo -e "${BOLD}${GREEN}✅ JIM AI AGENT УСПЕШНО УСТАНОВЛЕН!${END}"
echo -e "${BOLD}${GREEN}═══════════════════════════════════════════════════════════════════════════${END}"
echo -e ""
echo -e "${CYAN}📁 Директория: $JIM_DIR${END}"
echo -e "${CYAN}🔑 API ключ: $JIM_DIR/.env${END}"
echo -e "${CYAN}📝 Промпт: $JIM_DIR/system_prompt.txt${END}"
echo -e ""
echo -e "${BOLD}🚀 Запуск:${END}"
echo -e "   ${GREEN}jim${END}"
echo -e ""
echo -e "${BOLD}🔄 Обновление:${END}"
echo -e "   ${GREEN}jim -update${END}"
echo -e ""
echo -e "${BOLD}ℹ️  Справка:${END}"
echo -e "   ${GREEN}jim -h${END}"
echo -e ""
echo -e "${YELLOW}⚠️  Перезагрузите терминал или выполните: source ~/.bashrc${END}"
echo -e "${BOLD}${GREEN}═══════════════════════════════════════════════════════════════════════════${END}"