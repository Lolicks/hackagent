#!/bin/bash
# ============================================================
# Jim AI Agent - Универсальный установщик
# Работает на Kali Linux, Ubuntu, Debian, Parrot OS
# ============================================================

set -e

# Цвета для красивого вывода
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
CYAN='\033[96m'
BOLD='\033[1m'
END='\033[0m'

clear
echo -e "${BOLD}${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║              ██╗ ██╗███╗   ███╗    █████╗ ██╗     ███████╗███╗   ██╗████████╗  ║"
echo "║              ██║ ██║████╗ ████║   ██╔══██╗██║     ██╔════╝████╗  ██║╚══██╔══╝  ║"
echo "║              ██║ ██║██╔████╔██║   ███████║██║     █████╗  ██╔██╗ ██║   ██║     ║"
echo "║              ██║ ██║██║╚██╔╝██║   ██╔══██║██║     ██╔══╝  ██║╚██╗██║   ██║     ║"
echo "║              ███████║██║ ╚═╝ ██║██╗██║  ██║███████╗███████╗██║ ╚████║   ██║     ║"
echo "║              ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝     ║"
echo "║                                                                           ║"
echo "║                    🤖 JIM AI AGENT - УСТАНОВЩИК 🤖                         ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo -e "${END}"

# ============================================================
# 1. ОПРЕДЕЛЕНИЕ ДИРЕКТОРИЙ
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JIM_DIR="$HOME/.jim"
BIN_DIR="$HOME/.local/bin"
JIM_CMD="$BIN_DIR/jim"

echo -e "\n${BLUE}📁 [1/8] Настройка директорий...${END}"

# Создаём директории
mkdir -p "$JIM_DIR"
mkdir -p "$BIN_DIR"
echo -e "${GREEN}   ✅ Директория Jim: $JIM_DIR${END}"
echo -e "${GREEN}   ✅ Директория bin: $BIN_DIR${END}"

# ============================================================
# 2. КОПИРОВАНИЕ ФАЙЛОВ
# ============================================================

echo -e "\n${BLUE}📄 [2/8] Копирование файлов...${END}"

# Ищем основной файл (может называться по-разному)
if [ -f "$SCRIPT_DIR/jim.py" ]; then
    cp "$SCRIPT_DIR/jim.py" "$JIM_DIR/"
    echo -e "${GREEN}   ✅ Скопирован jim.py${END}"
elif [ -f "$SCRIPT_DIR/deepseek_chat.py" ]; then
    cp "$SCRIPT_DIR/deepseek_chat.py" "$JIM_DIR/jim.py"
    echo -e "${GREEN}   ✅ Скопирован deepseek_chat.py как jim.py${END}"
else
    echo -e "${RED}   ❌ Не найден файл с кодом агента!${END}"
    exit 1
fi

# Копируем system_prompt.txt если есть
if [ -f "$SCRIPT_DIR/system_prompt.txt" ]; then
    cp "$SCRIPT_DIR/system_prompt.txt" "$JIM_DIR/"
    echo -e "${GREEN}   ✅ Скопирован system_prompt.txt${END}"
fi

# ============================================================
# 3. НАСТРОЙКА API КЛЮЧА
# ============================================================

echo -e "\n${BLUE}🔑 [3/8] Настройка API ключа...${END}"

if [ ! -f "$JIM_DIR/.env" ]; then
    echo -e "${YELLOW}   📝 Введите ваш OpenRouter API ключ${END}"
    echo -e "${YELLOW}   (получить можно на https://openrouter.ai/keys)${END}"
    echo -ne "${CYAN}   🔑 API Key: ${END}"
    read API_KEY
    
    if [ -n "$API_KEY" ]; then
        echo "OPENROUTER_API_KEY=$API_KEY" > "$JIM_DIR/.env"
        echo -e "${GREEN}   ✅ API ключ сохранён${END}"
    else
        echo -e "${RED}   ❌ Ключ не введён!${END}"
        exit 1
    fi
else
    echo -e "${GREEN}   ✅ .env уже существует${END}"
fi

# ============================================================
# 4. СОЗДАНИЕ ГЛОБАЛЬНОЙ КОМАНДЫ
# ============================================================

echo -e "\n${BLUE}🔗 [4/8] Создание глобальной команды 'jim'...${END}"

cat > "$JIM_CMD" << 'EOF'
#!/bin/bash
# Jim AI Agent - глобальная команда

# Определяем пути
JIM_DIR="$HOME/.jim"
SCRIPT_FILE="$JIM_DIR/jim.py"
ENV_FILE="$JIM_DIR/.env"

# Проверяем наличие файлов
if [ ! -f "$SCRIPT_FILE" ]; then
    echo "❌ Ошибка: Jim не найден в $JIM_DIR"
    echo "   Переустановите: rm -rf $JIM_DIR && curl -sSL https://raw.githubusercontent.com/Lolicks/hackagent/main/install.sh | bash"
    exit 1
fi

# Переходим в директорию и запускаем
cd "$JIM_DIR"
python3 "$SCRIPT_FILE" "$@"
EOF

chmod +x "$JIM_CMD"
echo -e "${GREEN}   ✅ Команда создана: $JIM_CMD${END}"

# ============================================================
# 5. НАСТРОЙКА PATH
# ============================================================

echo -e "\n${BLUE}📝 [5/8] Настройка PATH...${END}"

# Проверяем, есть ли BIN_DIR в PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    # Добавляем в .bashrc
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        echo -e "${GREEN}   ✅ Добавлено в ~/.bashrc${END}"
    fi
    
    # Добавляем в .zshrc (для Kali Linux по умолчанию zsh)
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.zshrc 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        echo -e "${GREEN}   ✅ Добавлено в ~/.zshrc${END}"
    fi
    
    # Экспортируем для текущей сессии
    export PATH="$HOME/.local/bin:$PATH"
    echo -e "${GREEN}   ✅ PATH обновлён для текущей сессии${END}"
else
    echo -e "${GREEN}   ✅ PATH уже настроен${END}"
fi

# ============================================================
# 6. УСТАНОВКА ЗАВИСИМОСТЕЙ
# ============================================================

echo -e "\n${BLUE}🐍 [6/8] Установка Python зависимостей...${END}"

# Проверяем pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}   ⚠️ pip3 не найден, устанавливаю...${END}"
    sudo apt update -qq
    sudo apt install -y python3-pip
fi

# Устанавливаем пакеты
pip3 install --quiet --upgrade openai python-dotenv 2>/dev/null || pip install --quiet --upgrade openai python-dotenv
echo -e "${GREEN}   ✅ openai, python-dotenv установлены${END}"

# ============================================================
# 7. ПРОВЕРКА СИСТЕМНЫХ УТИЛИТ
# ============================================================

echo -e "\n${BLUE}🛠️ [7/8] Проверка системных утилит...${END}"

UTILS="nmap sqlmap gobuster nikto whatweb"
MISSING=""

for util in $UTILS; do
    if command -v $util &> /dev/null; then
        echo -e "${GREEN}   ✅ $util${END}"
    else
        echo -e "${RED}   ❌ $util (опционально)${END}"
        MISSING="$MISSING $util"
    fi
done

if [ -n "$MISSING" ]; then
    echo -e "\n${YELLOW}   ⚠️ Некоторые утилиты не установлены. Установите при необходимости:${END}"
    echo -e "${CYAN}   sudo apt install$MISSING${END}"
fi

# ============================================================
# 8. СОЗДАНИЕ ПРОМПТА ПО УМОЛЧАНИЮ
# ============================================================

echo -e "\n${BLUE}📝 [8/8] Настройка промпта...${END}"

if [ ! -f "$JIM_DIR/system_prompt.txt" ]; then
    cat > "$JIM_DIR/system_prompt.txt" << 'EOF'
Ты - Jim, автономный ИИ-агент для пентеста Kali Linux.

## ТВОЙ АЛГОРИТМ:
1. Получи цель от пользователя
2. Выбери подходящие утилиты (nmap, sqlmap, gobuster, nikto, whatweb)
3. Проанализируй вывод каждой утилиты
4. Прими решение о следующих действиях
5. Выдай итоговый отчёт

Будь профессиональным и дружелюбным! Твоё имя - Jim.
EOF
    echo -e "${GREEN}   ✅ Создан system_prompt.txt${END}"
else
    echo -e "${GREEN}   ✅ system_prompt.txt уже существует${END}"
fi

# ============================================================
# ИТОГ
# ============================================================

echo -e "\n${BOLD}${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║              ✅ JIM AI AGENT УСПЕШНО УСТАНОВЛЕН! ✅                         ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo -e "${END}"

echo -e "\n${CYAN}📁 Установлено в: $JIM_DIR${END}"
echo -e "${CYAN}🔑 API ключ: $JIM_DIR/.env${END}"
echo -e "${CYAN}📝 Промпт: $JIM_DIR/system_prompt.txt${END}"

echo -e "\n${BOLD}🚀 ЗАПУСК:${END}"
echo -e "   ${GREEN}jim${END}"

echo -e "\n${BOLD}🔄 ОБНОВЛЕНИЕ:${END}"
echo -e "   ${GREEN}rm -rf ~/.jim && git clone https://github.com/Lolicks/hackagent.git ~/jim-temp && cp ~/jim-temp/* ~/.jim/ && rm -rf ~/jim-temp${END}"

echo -e "\n${BOLD}🗑️ УДАЛЕНИЕ:${END}"
echo -e "   ${GREEN}rm -rf ~/.jim ~/.local/bin/jim${END}"

echo -e "\n${YELLOW}⚠️  ВАЖНО: Перезагрузите терминал или выполните:${END}"
echo -e "   ${CYAN}source ~/.zshrc${END}"

echo -e "\n${BOLD}${GREEN}═══════════════════════════════════════════════════════════════════════════${END}"

# Проверка установки
if command -v jim &> /dev/null; then
    echo -e "\n${GREEN}✅ Команда 'jim' уже доступна!${END}"
    echo -e "\n${CYAN}💡 Попробуйте: jim${END}"
else
    echo -e "\n${YELLOW}⚠️ Команда 'jim' будет доступна после перезагрузки терминала${END}"
fi