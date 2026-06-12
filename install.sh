#!/bin/bash
# ============================================================
# Jim AI Agent - Универсальный установщик
# Скачивает репозиторий автоматически
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
# 0. ПРОВЕРКА ИНСТРУМЕНТОВ
# ============================================================

echo -e "\n${BLUE}🔧 [0/9] Проверка инструментов...${END}"

# Проверяем наличие git или wget/curl
HAS_GIT=false
HAS_CURL=false
HAS_WGET=false

if command -v git &> /dev/null; then
    HAS_GIT=true
    echo -e "${GREEN}   ✅ git установлен${END}"
fi

if command -v curl &> /dev/null; then
    HAS_CURL=true
    echo -e "${GREEN}   ✅ curl установлен${END}"
fi

if command -v wget &> /dev/null; then
    HAS_WGET=true
    echo -e "${GREEN}   ✅ wget установлен${END}"
fi

if [ "$HAS_GIT" = false ] && [ "$HAS_CURL" = false ] && [ "$HAS_WGET" = false ]; then
    echo -e "${RED}   ❌ Не найден ни git, ни curl, ни wget${END}"
    echo -e "${YELLOW}   Установите один из них: sudo apt install git${END}"
    exit 1
fi

# ============================================================
# 1. ОПРЕДЕЛЕНИЕ ДИРЕКТОРИЙ
# ============================================================

echo -e "\n${BLUE}📁 [1/9] Настройка директорий...${END}"

JIM_DIR="$HOME/.jim"
BIN_DIR="$HOME/.local/bin"
JIM_CMD="$BIN_DIR/jim"
TEMP_DIR="/tmp/jim-install-$$"

# Создаём директории
mkdir -p "$JIM_DIR"
mkdir -p "$BIN_DIR"
echo -e "${GREEN}   ✅ Директория Jim: $JIM_DIR${END}"
echo -e "${GREEN}   ✅ Директория bin: $BIN_DIR${END}"

# ============================================================
# 2. СКАЧИВАНИЕ РЕПОЗИТОРИЯ
# ============================================================

echo -e "\n${BLUE}📦 [2/9] Скачивание репозитория...${END}"

REPO_URL="https://github.com/Lolicks/hackagent.git"

# Удаляем временную папку если есть
rm -rf "$TEMP_DIR"

if [ "$HAS_GIT" = true ]; then
    echo -e "${CYAN}   Использую git...${END}"
    git clone --depth 1 "$REPO_URL" "$TEMP_DIR" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   ✅ Репозиторий склонирован через git${END}"
    else
        echo -e "${YELLOW}   ⚠️ Git clone не удался, пробую другие способы...${END}"
        HAS_GIT=false
    fi
fi

if [ "$HAS_GIT" = false ]; then
    if [ "$HAS_CURL" = true ]; then
        echo -e "${CYAN}   Использую curl...${END}"
        curl -sSL "https://github.com/Lolicks/hackagent/archive/refs/heads/master.zip" -o "$TEMP_DIR.zip"
        if command -v unzip &> /dev/null; then
            unzip -q "$TEMP_DIR.zip" -d "$TEMP_DIR"
            mv "$TEMP_DIR/hackagent-master/"* "$TEMP_DIR/" 2>/dev/null
            rm -f "$TEMP_DIR.zip"
            echo -e "${GREEN}   ✅ Репозиторий скачан через curl${END}"
        else
            echo -e "${RED}   ❌ unzip не установлен${END}"
            exit 1
        fi
    elif [ "$HAS_WGET" = true ]; then
        echo -e "${CYAN}   Использую wget...${END}"
        wget -q "https://github.com/Lolicks/hackagent/archive/refs/heads/master.zip" -O "$TEMP_DIR.zip"
        if command -v unzip &> /dev/null; then
            unzip -q "$TEMP_DIR.zip" -d "$TEMP_DIR"
            mv "$TEMP_DIR/hackagent-master/"* "$TEMP_DIR/" 2>/dev/null
            rm -f "$TEMP_DIR.zip"
            echo -e "${GREEN}   ✅ Репозиторий скачан через wget${END}"
        else
            echo -e "${RED}   ❌ unzip не установлен${END}"
            exit 1
        fi
    fi
fi

# Проверяем, что скачалось
if [ ! -f "$TEMP_DIR/install.sh" ] && [ ! -f "$TEMP_DIR/jim.py" ] && [ ! -f "$TEMP_DIR/deepseek_chat.py" ]; then
    echo -e "${RED}   ❌ Не удалось скачать репозиторий${END}"
    exit 1
fi
echo -e "${GREEN}   ✅ Репозиторий скачан в $TEMP_DIR${END}"

# ============================================================
# 3. КОПИРОВАНИЕ ФАЙЛОВ
# ============================================================

echo -e "\n${BLUE}📄 [3/9] Копирование файлов...${END}"

# Ищем основной файл
if [ -f "$TEMP_DIR/jim.py" ]; then
    cp "$TEMP_DIR/jim.py" "$JIM_DIR/"
    echo -e "${GREEN}   ✅ Скопирован jim.py${END}"
elif [ -f "$TEMP_DIR/deepseek_chat.py" ]; then
    cp "$TEMP_DIR/deepseek_chat.py" "$JIM_DIR/jim.py"
    echo -e "${GREEN}   ✅ Скопирован deepseek_chat.py как jim.py${END}"
else
    echo -e "${RED}   ❌ Не найден файл с кодом агента!${END}"
    exit 1
fi

# Копируем system_prompt.txt если есть
if [ -f "$TEMP_DIR/system_prompt.txt" ]; then
    cp "$TEMP_DIR/system_prompt.txt" "$JIM_DIR/"
    echo -e "${GREEN}   ✅ Скопирован system_prompt.txt${END}"
fi

# Очищаем временную папку
rm -rf "$TEMP_DIR"
echo -e "${GREEN}   ✅ Временные файлы удалены${END}"

# ============================================================
# 4. НАСТРОЙКА API КЛЮЧА
# ============================================================

echo -e "\n${BLUE}🔑 [4/9] Настройка API ключа...${END}"

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
# 5. СОЗДАНИЕ ГЛОБАЛЬНОЙ КОМАНДЫ
# ============================================================

echo -e "\n${BLUE}🔗 [5/9] Создание глобальной команды 'jim'...${END}"

cat > "$JIM_CMD" << 'EOF'
#!/bin/bash
# Jim AI Agent - глобальная команда

JIM_DIR="$HOME/.jim"
SCRIPT_FILE="$JIM_DIR/jim.py"

if [ ! -f "$SCRIPT_FILE" ]; then
    echo "❌ Ошибка: Jim не найден в $JIM_DIR"
    exit 1
fi

cd "$JIM_DIR"
python3 "$SCRIPT_FILE" "$@"
EOF

chmod +x "$JIM_CMD"
echo -e "${GREEN}   ✅ Команда создана: $JIM_CMD${END}"

# ============================================================
# 6. НАСТРОЙКА PATH
# ============================================================

echo -e "\n${BLUE}📝 [6/9] Настройка PATH...${END}"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        echo -e "${GREEN}   ✅ Добавлено в ~/.bashrc${END}"
    fi
    
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.zshrc 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        echo -e "${GREEN}   ✅ Добавлено в ~/.zshrc${END}"
    fi
    
    export PATH="$HOME/.local/bin:$PATH"
    echo -e "${GREEN}   ✅ PATH обновлён для текущей сессии${END}"
else
    echo -e "${GREEN}   ✅ PATH уже настроен${END}"
fi

# ============================================================
# 7. УСТАНОВКА ЗАВИСИМОСТЕЙ
# ============================================================

echo -e "\n${BLUE}🐍 [7/9] Установка Python зависимостей...${END}"

if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}   ⚠️ pip3 не найден, устанавливаю...${END}"
    sudo apt update -qq
    sudo apt install -y python3-pip
fi

pip3 install --quiet --upgrade openai python-dotenv 2>/dev/null || pip install --quiet --upgrade openai python-dotenv
echo -e "${GREEN}   ✅ openai, python-dotenv установлены${END}"

# ============================================================
# 8. ПРОВЕРКА СИСТЕМНЫХ УТИЛИТ
# ============================================================

echo -e "\n${BLUE}🛠️ [8/9] Проверка системных утилит...${END}"

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
# 9. СОЗДАНИЕ ПРОМПТА ПО УМОЛЧАНИЮ
# ============================================================

echo -e "\n${BLUE}📝 [9/9] Настройка промпта...${END}"

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
echo -e "   ${GREEN}bash <(curl -sSL https://raw.githubusercontent.com/Lolicks/hackagent/master/install.sh)${END}"

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