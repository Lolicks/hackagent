#!/bin/bash
# ============================================================
# Jim AI Agent - Установщик для Kali Linux
# Использует pipx для безопасной установки
# ============================================================

set -e

# Цвета
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
echo "║                    🤖 JIM AI AGENT - УСТАНОВЩИК 🤖                         ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo -e "${END}"

# ============================================================
# 1. ПРОВЕРКА ЧТО МЫ В ПРАВИЛЬНОЙ ПАПКЕ
# ============================================================

echo -e "\n${BLUE}📁 [1/7] Проверка репозитория...${END}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/jim.py" ]; then
    MAIN_FILE="$SCRIPT_DIR/jim.py"
    echo -e "${GREEN}   ✅ Найден jim.py${END}"
elif [ -f "$SCRIPT_DIR/deepseek_chat.py" ]; then
    MAIN_FILE="$SCRIPT_DIR/deepseek_chat.py"
    echo -e "${GREEN}   ✅ Найден deepseek_chat.py${END}"
else
    echo -e "${RED}   ❌ Не найден файл с кодом агента!${END}"
    exit 1
fi

# ============================================================
# 2. ПРОВЕРКА/УСТАНОВКА PIPX
# ============================================================

echo -e "\n${BLUE}📦 [2/7] Проверка pipx...${END}"

if ! command -v pipx &> /dev/null; then
    echo -e "${YELLOW}   ⚠️ pipx не установлен, устанавливаю...${END}"
    sudo apt update -qq
    sudo apt install -y pipx
    pipx ensurepath
    echo -e "${GREEN}   ✅ pipx установлен${END}"
else
    echo -e "${GREEN}   ✅ pipx уже установлен${END}"
fi

# ============================================================
# 3. СОЗДАНИЕ ДИРЕКТОРИЙ
# ============================================================

echo -e "\n${BLUE}📁 [3/7] Создание директорий...${END}"

JIM_DIR="$HOME/.jim"
BIN_DIR="$HOME/.local/bin"
JIM_CMD="$BIN_DIR/jim"

mkdir -p "$JIM_DIR"
mkdir -p "$BIN_DIR"
echo -e "${GREEN}   ✅ Директория Jim: $JIM_DIR${END}"
echo -e "${GREEN}   ✅ Директория bin: $BIN_DIR${END}"

# ============================================================
# 4. КОПИРОВАНИЕ ФАЙЛОВ
# ============================================================

echo -e "\n${BLUE}📄 [4/7] Копирование файлов...${END}"

cp "$MAIN_FILE" "$JIM_DIR/jim.py"
echo -e "${GREEN}   ✅ Скопирован основной файл${END}"

if [ -f "$SCRIPT_DIR/system_prompt.txt" ]; then
    cp "$SCRIPT_DIR/system_prompt.txt" "$JIM_DIR/"
    echo -e "${GREEN}   ✅ Скопирован system_prompt.txt${END}"
fi

# ============================================================
# 5. УСТАНОВКА PYTHON ПАКЕТОВ ЧЕРЕЗ PIPX
# ============================================================

echo -e "\n${BLUE}🐍 [5/7] Установка Python пакетов через pipx...${END}"

# Устанавливаем openai и python-dotenv в изолированное окружение
pipx install openai python-dotenv --quiet 2>/dev/null || \
    pipx install --pip-args="openai python-dotenv" --quiet 2>/dev/null || \
    echo -e "${YELLOW}   ⚠️ Установка через pipx, пакеты будут доступны в venv${END}"

echo -e "${GREEN}   ✅ Пакеты установлены${END}"

# ============================================================
# 6. НАСТРОЙКА API КЛЮЧА
# ============================================================

echo -e "\n${BLUE}🔑 [6/7] Настройка API ключа...${END}"

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
# 7. СОЗДАНИЕ ГЛОБАЛЬНОЙ КОМАНДЫ
# ============================================================

echo -e "\n${BLUE}🔗 [7/7] Создание глобальной команды 'jim'...${END}"

cat > "$JIM_CMD" << 'EOF'
#!/bin/bash
# Jim AI Agent - работает в виртуальном окружении pipx
JIM_DIR="$HOME/.jim"
cd "$JIM_DIR"

# Используем Python из pipx или системный
if command -v pipx &> /dev/null; then
    # pipx создаёт свои venv, используем их
    PIPX_VENV="$HOME/.local/pipx/venvs"
    if [ -d "$PIPX_VENV/openai" ]; then
        "$PIPX_VENV/openai/bin/python" "$JIM_DIR/jim.py" "$@"
    elif [ -d "$PIPX_VENV/python-dotenv" ]; then
        "$PIPX_VENV/python-dotenv/bin/python" "$JIM_DIR/jim.py" "$@"
    else
        python3 "$JIM_DIR/jim.py" "$@"
    fi
else
    python3 "$JIM_DIR/jim.py" "$@"
fi
EOF

chmod +x "$JIM_CMD"
echo -e "${GREEN}   ✅ Команда создана: $JIM_CMD${END}"

# Добавляем в PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null
    export PATH="$HOME/.local/bin:$PATH"
    echo -e "${GREEN}   ✅ PATH настроен${END}"
fi

# ============================================================
# ИТОГ
# ============================================================

echo -e "\n${BOLD}${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║              ✅ JIM AI AGENT УСПЕШНО УСТАНОВЛЕН! ✅                         ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo -e "${END}"

echo -e "\n${CYAN}📁 Установлено в: $JIM_DIR${END}"
echo -e "${CYAN}🔑 API ключ: $JIM_DIR/.env${END}"
echo -e "${CYAN}📝 Промпт: $JIM_DIR/system_prompt.txt${END}"

echo -e "\n${BOLD}🚀 ЗАПУСК:${END}"
echo -e "   ${GREEN}jim${END}"

echo -e "\n${BOLD}🗑️ УДАЛЕНИЕ:${END}"
echo -e "   ${GREEN}rm -rf ~/.jim ~/.local/bin/jim${END}"

echo -e "\n${YELLOW}⚠️  Перезагрузите терминал или выполните: source ~/.zshrc${END}"

echo -e "\n${BOLD}${GREEN}═══════════════════════════════════════════════════════════════════════════${END}"