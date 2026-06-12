#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                              ║
║    ██╗ ██╗███╗   ███╗         █████╗ ██╗███████╗███╗   ██╗████████╗                        ║
║    ██║ ██║████╗ ████║        ██╔══██╗██║██╔════╝████╗  ██║╚══██╔══╝                        ║
║    ██║ ██║██╔████╔██║        ███████║██║█████╗  ██╔██╗ ██║   ██║                           ║
║    ██║ ██║██║╚██╔╝██║        ██╔══██║██║██╔══╝  ██║╚██╗██║   ██║                           ║
║    ███████║██║ ╚═╝ ██║██╗     ██║  ██║██║███████╗██║ ╚████║   ██║                           ║
║    ╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝                           ║
║                                                                                              ║
║                         █████╗ ██╗       ███████╗███╗   ██╗████████╗                         ║
║                        ██╔══██╗██║       ██╔════╝████╗  ██║╚══██╔══╝                         ║
║                        ███████║██║       █████╗  ██╔██╗ ██║   ██║                            ║
║                        ██╔══██║██║       ██╔══╝  ██║╚██╗██║   ██║                            ║
║                        ██║  ██║███████╗  ███████╗██║ ╚████║   ██║                            ║
║                        ╚═╝  ╚═╝╚══════╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝                            ║
║                                                                                              ║
║                         🤖 JIM - ИНТЕЛЛЕКТУАЛЬНЫЙ ИИ-АГЕНТ 🤖                                ║
║                      Понимаю естественный язык | Полный анализ | Сохранение сессий          ║
║                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import subprocess
import json
import re
import shutil
import time
import threading
import signal
import urllib.request
import urllib.parse
from urllib.error import HTTPError
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================
# ОБРАБОТКА СИГНАЛОВ
# ============================================================

current_process = None
interrupted = False
session_start_time = None
paused = False

def signal_handler(sig, frame):
    global interrupted, current_process, session_start_time
    interrupted = True
    elapsed = ""
    if session_start_time:
        elapsed = f" (работал {int(time.time() - session_start_time)}с)"
    
    print(f"\n\n{Colors.BOLD}{Colors.YELLOW}⏸️  ОСТАНОВКА...{elapsed}{Colors.END}")
    
    if current_process:
        try:
            print(f"{Colors.DIM}Завершаю процесс...{Colors.END}")
            current_process.terminate()
            time.sleep(0.5)
            if current_process.poll() is None:
                current_process.kill()
        except Exception as e:
            pass
    
    print(f"{Colors.YELLOW}Введите /exit для выхода или команду для продолжения{Colors.END}\n")

signal.signal(signal.SIGINT, signal_handler)

# ============================================================
# ВЕРСИЯ И АРГУМЕНТЫ
# ============================================================

VERSION = "3.0.0"

def update_jim():
    print("\n" + "="*70)
    print(" 🔄 ОБНОВЛЕНИЕ JIM ".center(70, "="))
    print("="*70 + "\n")
    jim_dir = os.path.expanduser("~/.jim")
    repo_url = "https://github.com/Lolicks/hackagent.git"
    temp_dir = "/tmp/jim-update"
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print(" 📦 Загрузка...")
        subprocess.run(["git", "clone", "--depth", "1", repo_url, temp_dir], check=True, capture_output=True)
        print(" 📄 Обновление...")
        shutil.copy2(f"{temp_dir}/jim.py", f"{jim_dir}/jim.py")
        shutil.copy2(f"{temp_dir}/system_prompt.txt", f"{jim_dir}/")
        shutil.rmtree(temp_dir)
        print("\n ✅ Обновление завершено!")
        return True
    except Exception as e:
        print(f" ❌ Ошибка: {e}")
        return False

args = sys.argv[1:]
AUTO_MODE = False
DRY_RUN = False
PROFILE = "normal"

for arg in args:
    if arg in ["-v", "--version"]:
        print(f"JIM AI Agent v{VERSION}")
        sys.exit(0)
    elif arg in ["-h", "--help"]:
        print("""
╔════════════════════════════════════════════════════════════════════╗
║                         JIM - СПРАВКА                              ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  JIM - интеллектуальный ИИ-агент для пентеста                     ║
║  Просто говорите что нужно естественным языком                    ║
║                                                                    ║
║  Примеры:                                                         ║
║    > проверь site.com/page?id=1 на SQL инъекции                   ║
║    > найди открытые порты на 192.168.1.1                          ║
║    > просканируй example.com на уязвимости                        ║
║    > sqlmap                                                        ║
║                                                                    ║
║  Команды:                                                         ║
║    /help      - справка                                           ║
║    /status    - статус сессии                                     ║
║    /stop      - остановить сканирование                           ║
║    /continue  - продолжить                                        ║
║    /report    - итоговый отчёт                                    ║
║    /context   - показать сохранённые цели                         ║
║    /reset     - очистить память                                   ║
║    /exit      - выход                                             ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")
        sys.exit(0)
    elif arg in ["-a", "--auto"]:
        AUTO_MODE = True
    elif arg == "--dry-run":
        DRY_RUN = True
    elif arg.startswith("--profile="):
        PROFILE = arg.split("=")[1]
    elif arg in ["-u", "--update"]:
        sys.exit(0 if update_jim() else 1)

# ============================================================
# ЦВЕТА
# ============================================================

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    END = '\033[0m'
    
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    
    ICON_AGENT = "🤖"
    ICON_USER = "👤"
    ICON_TOOL = "⚙️"
    ICON_ANALYSIS = "🔍"
    ICON_REPORT = "📊"
    ICON_INFO = "ℹ️"
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"
    ICON_TARGET = "🎯"
    ICON_BUG = "🐛"
    ICON_SHIELD = "🛡️"
    ICON_RESET = "🧹"
    ICON_THINKING = "💭"
    ICON_DB = "🗄️"
    ICON_PORT = "🔌"
    ICON_FOLDER = "📁"

# ============================================================
# UI КОМПОНЕНТЫ
# ============================================================

class UI:
    @staticmethod
    def separator(char: str = "─", length: int = 70):
        print(f"{Colors.DIM}{char * length}{Colors.END}")
    
    @staticmethod
    def header(text: str, icon: str = "📋"):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{icon} {text.center(66)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}")
    
    @staticmethod
    def success(text: str):
        print(f"{Colors.GREEN}{Colors.ICON_SUCCESS} {text}{Colors.END}")
    
    @staticmethod
    def error(text: str):
        print(f"{Colors.RED}{Colors.ICON_ERROR} {text}{Colors.END}")
    
    @staticmethod
    def warning(text: str):
        print(f"{Colors.YELLOW}{Colors.ICON_WARNING} {text}{Colors.END}")
    
    @staticmethod
    def info(text: str):
        print(f"{Colors.CYAN}{Colors.ICON_INFO} {text}{Colors.END}")
    
    @staticmethod
    def thinking(text: str, duration: float = 0.5):
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            sys.stdout.write(f"\r{Colors.BLUE}{Colors.ICON_THINKING} {chars[i % len(chars)]} {text}{Colors.END}")
            sys.stdout.flush()
            time.sleep(0.05)
            i += 1
        sys.stdout.write("\r" + " " * (len(text) + 5) + "\r")
    
    @staticmethod
    def progress_bar(percent: int, width: int = 40):
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        color = Colors.GREEN if percent < 70 else Colors.YELLOW if percent < 90 else Colors.RED
        print(f"{color}{bar}{Colors.END} {percent}%")

# ============================================================
# ЗАГРУЗКА НАСТРОЕК
# ============================================================

def load_api_key():
    env_paths = [
        os.path.expanduser("~/.jim/.env"),
        os.path.join(os.getcwd(), ".env")
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith("OPENROUTER_API_KEY="):
                        return line.strip().split("=", 1)[1]
    return None

def load_system_prompt():
    prompt_paths = [
        os.path.join(os.getcwd(), "system_prompt.txt"),
        os.path.expanduser("~/.jim/system_prompt.txt")
    ]
    for prompt_path in prompt_paths:
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
    return """Ты - Jim, интеллектуальный ИИ-агент для пентеста. Понимаешь естественный язык. Будь полезным и понятным."""

def ensure_directories():
    dirs = [
        os.path.expanduser("~/.jim"),
        os.path.expanduser("~/.jim/sessions"),
        os.path.expanduser("~/.jim/reports"),
        os.path.expanduser("~/.jim/logs"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def context_file_path() -> str:
    return os.path.expanduser("~/.jim/targets.json")


def load_context_targets() -> List[str]:
    path = context_file_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                targets = json.load(f)
                if isinstance(targets, list):
                    return targets[-5:]
        except Exception:
            pass
    return []


def save_context_targets(targets: List[str]):
    path = context_file_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(targets[-5:], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def is_admin_path(target: str) -> bool:
    path = target.lower()
    return any(token in path for token in ['/admin', '/login', '/wp-admin', '/administrator', '/user/login'])


def is_static_file(target: str) -> bool:
    return bool(re.search(r'\.(html|htm|css|js|png|jpg|jpeg|gif|svg|ico|pdf|txt)(\?|$)', target.lower()))

API_KEY = load_api_key()
SYSTEM_PROMPT = load_system_prompt()
CHAT_PROMPT = "Ты - Jim, интеллектуальный ИИ-агент для пентеста. Отвечай прямо и понятно на вопросы пользователя. Не используй JSON для обычных диалогов."
ensure_directories()

# ============================================================
# ПРОВЕРКА API КЛЮЧА
# ============================================================

def check_api_key():
    UI.header("🔑 ПРОВЕРКА API КЛЮЧА", "🔑")
    
    if not API_KEY:
        UI.error("API ключ не найден!")
        UI.info("Создайте файл ~/.jim/.env с содержимым:")
        print(f"   OPENROUTER_API_KEY=sk-or-v1-ваш_ключ")
        UI.info("Получить ключ: https://openrouter.ai/keys")
        return False
    
    if not API_KEY.startswith("sk-or-v1-"):
        UI.error("Неверный формат API ключа!")
        UI.info("Ключ должен начинаться с 'sk-or-v1-'")
        return False
    
    UI.success("API ключ найден")
    
    UI.thinking("Проверка подключения...", 0.5)
    
    try:
        import openai
        test_client = openai.OpenAI(
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
            timeout=10
        )
        response = test_client.chat.completions.create(
            model="deepseek/deepseek-v4-flash",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
            temperature=0.0
        )
        UI.success("API подключение успешно")
    except Exception as e:
        UI.error(f"Ошибка подключения: {str(e)[:50]}")
        return False

    UI.thinking("Проверяю баланс...", 0.5)
    try:
        request = urllib.request.Request(
            "https://openrouter.ai/api/v1/credits",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(request, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            balance = None
            if isinstance(data, dict):
                balance = data.get('balance') or data.get('credits') or data.get('available')
            if balance is None:
                UI.warning("Не удалось определить баланс, но ключ действителен")
            elif isinstance(balance, (int, float)) and balance <= 0:
                UI.error("Баланс равен нулю или отрицательный. Пополните счёт.")
                return False
            else:
                UI.success(f"Баланс доступен: {balance}")
    except HTTPError as e:
        if e.code == 402:
            UI.error("Баланс недостаточен (402). Пополните счёт.")
            return False
        UI.error(f"Ошибка проверки баланса: HTTP {e.code}")
        return False
    except Exception as e:
        UI.warning(f"Проверка баланса не удалась: {str(e)[:50]}")

    return True

# ============================================================
# УМНЫЙ ВЫБОР ФЛАГОВ
# ============================================================

def get_nmap_flags(context: str) -> str:
    """Выбрать флаги для nmap на основе контекста"""
    context_lower = context.lower() if isinstance(context, str) else str(context).lower()
    
    if "быстрый" in context_lower or "quick" in context_lower:
        return "-F --open"
    elif "все порты" in context_lower or "full" in context_lower or "all" in context_lower:
        return "-p- --open"
    elif "агрессивный" in context_lower or "aggressive" in context_lower or "интенсив" in context_lower:
        return "-sV -sC -O -A"
    elif "тихий" in context_lower or "stealth" in context_lower or "скрыт" in context_lower:
        return "-sS -Pn -T2 -f"
    else:
        return "-sV --open"

def get_sqlmap_flags(context: str) -> str:
    """Выбрать флаги для sqlmap на основе контекста и явно указанных флагов"""
    context_lower = context.lower() if isinstance(context, str) else str(context).lower()
    
    # Сначала проверяем явно указанные флаги
    explicit_flags = []
    
    # Извлекаем явные флаги типа --forms, --crawl и т.д.
    flag_patterns = [r'--\w+']
    for pattern in flag_patterns:
        explicit_flags.extend(re.findall(pattern, context_lower))
    
    base_flags = "--batch --dbs --level=1"
    
    # Если есть явные флаги, используем их вместе с базовыми
    if explicit_flags:
        # Удаляем дубликаты и складываем
        explicit_flags_str = " ".join(set(explicit_flags))
        return f"{base_flags} {explicit_flags_str}"
    
    # Иначе используем логику по контексту
    if "быстрый" in context_lower or "quick" in context_lower:
        return "--batch --current-db --level=1"
    elif "полный" in context_lower or "full" in context_lower or "agressive" in context_lower or "все" in context_lower:
        return "--batch --dbs --tables --level=3 --risk=2"
    elif "waf" in context_lower or "защита" in context_lower or "брандмауэр" in context_lower:
        return "--batch --dbs --level=3 --random-agent --tamper=space2comment,charencode"
    elif "тихий" in context_lower or "stealth" in context_lower or "медленно" in context_lower:
        return "--batch --dbs --delay=5 --random-agent"
    elif "blind" in context_lower or "time-based" in context_lower or "time based" in context_lower:
        return "--batch --dbs --technique=T --level=2"
    elif "error" in context_lower or "ошибк" in context_lower:
        return "--batch --dbs --technique=E --level=1"
    else:
        return base_flags

# ============================================================
# ЗАПУСК КОМАНД
# ============================================================

def run_command(cmd: str, timeout: int = 300) -> Dict:
    global current_process, interrupted, session_start_time
    
    print(f"{Colors.DIM}└─$ {cmd}{Colors.END}")
    UI.separator("─")
    
    interrupted = False
    output_lines = []
    start_time = time.time()
    if not session_start_time:
        session_start_time = start_time
    
    try:
        current_process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in iter(current_process.stdout.readline, ''):
            if interrupted:
                print(f"\n\n{Colors.BOLD}{Colors.YELLOW}⏹️  ОСТАНОВКА{Colors.END}")
                print(f"{Colors.DIM}Завершаю процесс...{Colors.END}")
                try:
                    current_process.terminate()
                    current_process.wait(timeout=2)
                except:
                    try:
                        current_process.kill()
                    except:
                        pass
                
                elapsed = int(time.time() - start_time)
                print(f"{Colors.CYAN}Собрано {len(output_lines)} строк за {elapsed}с{Colors.END}")
                print(f"{Colors.ICON_SUCCESS} Результаты сохранены{Colors.END}\n")
                return {"success": False, "output": "\n".join(output_lines), "interrupted": True, "duration": elapsed}
            
            if line:
                output_lines.append(line.rstrip())
                if 'vulnerable' in line.lower() and 'not' not in line.lower():
                    print(f"{Colors.BG_RED}{Colors.BOLD}{Colors.WHITE}{line.rstrip()}{Colors.END}")
                elif 'open' in line.lower() and 'tcp' in line.lower():
                    print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                elif 'error' in line.lower():
                    print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                elif 'database' in line.lower():
                    print(f"{Colors.CYAN}{line.rstrip()}{Colors.END}")
                else:
                    print(f"{Colors.DIM}{line.rstrip()}{Colors.END}")
        
        current_process.wait(timeout=timeout)
        elapsed = time.time() - start_time
        return {
            "success": current_process.returncode == 0,
            "output": "\n".join(output_lines),
            "duration": elapsed,
            "interrupted": False
        }
    except subprocess.TimeoutExpired:
        current_process.terminate()
        return {"success": False, "output": "\n".join(output_lines), "duration": timeout, "interrupted": False}
    finally:
        current_process = None

# ============================================================
# АНАЛИЗ ВЫВОДА УТИЛИТ
# ============================================================

class OutputAnalyzer:
    @staticmethod
    def analyze_nmap(output: str) -> Dict:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        ports = re.findall(r'(\d+)/tcp\s+open\s+(\w+)', output)
        if ports:
            analysis["found"] = True
            analysis["summary"] = f"🔓 Найдено {len(ports)} открытых портов"
            for port, service in ports[:10]:
                analysis["details"].append(f"Порт {port}: {service}")
                if port in ["80", "443", "8080"]:
                    analysis["insights"].append(f"🌐 Веб-сервер на порту {port}")
                elif service in ["mysql", "postgresql"]:
                    analysis["insights"].append(f"🗄️ База данных ({service}) на порту {port}")
        else:
            analysis["summary"] = "🔒 Открытых портов не найдено"
        
        return analysis
    
    @staticmethod
    def analyze_sqlmap(output: str) -> Dict:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        if "vulnerable" in output.lower() and "does not appear to be injectable" not in output.lower():
            analysis["found"] = True
            analysis["summary"] = "🐛 SQL-инъекция ОБНАРУЖЕНА!"
            
            if "boolean" in output.lower():
                analysis["details"].append("Тип: Boolean-based Blind")
            if "union" in output.lower():
                analysis["details"].append("Тип: Union-based")
            if "time" in output.lower():
                analysis["details"].append("Тип: Time-based Blind")
            
            dbs = re.findall(r'\[\*\*\]\s+(\w+)', output)
            if dbs:
                analysis["details"].append(f"Базы данных: {', '.join(dbs[:5])}")
                analysis["insights"].append(f"📊 Обнаружено {len(dbs)} баз данных")
        else:
            analysis["summary"] = "🛡️ SQL-инъекция НЕ обнаружена"
            if "waf" in output.lower():
                analysis["insights"].append("🛡️ Обнаружена WAF защита")
        
        return analysis
    
    @staticmethod
    def analyze_whatweb(output: str) -> Dict:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        clean = re.sub(r'\x1b\[[0-9;]*m', '', output)
        
        ignore = ['429', 'hcdn', 'GERMANY', 'DE', 'cloudflare', 'ddos', 'Too Many']
        techs = re.findall(r'\[(.*?)\]', clean)
        real_techs = []
        
        for t in techs:
            if not any(i in t for i in ignore) and len(t) < 50 and len(t) > 1 and 'http' not in t.lower():
                real_techs.append(t)
        
        real_techs = list(dict.fromkeys(real_techs))
        
        if real_techs:
            analysis["found"] = True
            analysis["summary"] = f"🔧 Обнаружено {len(real_techs)} технологий"
            for t in real_techs[:8]:
                analysis["details"].append(t)
        else:
            analysis["summary"] = "❓ Технологии не определены"
            ip = re.search(r'IP\[([0-9.]+)\]', clean)
            if ip:
                analysis["insights"].append(f"🌐 IP сервера: {ip.group(1)}")
        
        return analysis
    
    @staticmethod
    def analyze_gobuster(output: str) -> Dict:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        dirs = re.findall(r'/(\S+)\s+\(Status:\s+(\d+)\)', output)
        interesting = [d for d in dirs if d[1] in ["200", "301", "302", "401", "403"]]
        
        if interesting:
            analysis["found"] = True
            analysis["summary"] = f"📁 Найдено {len(interesting)} интересных директорий"
            for path, status in interesting[:15]:
                analysis["details"].append(f"/{path} (HTTP {status})")
                if status == "200":
                    analysis["insights"].append(f"📄 Доступно: /{path}")
        else:
            analysis["summary"] = "📭 Интересных директорий не найдено"
        
        return analysis
    
    @staticmethod
    def analyze_nikto(output: str) -> Dict:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        vulns = re.findall(r'\+ (.*?):', output)
        critical = [v for v in vulns if any(k in v.lower() for k in ['cve', 'vulnerable', 'xss', 'sql'])]
        
        if critical:
            analysis["found"] = True
            analysis["summary"] = f"⚠️ Обнаружено {len(critical)} уязвимостей"
            for v in critical[:5]:
                analysis["details"].append(v[:80])
        else:
            analysis["summary"] = "🛡️ Очевидных уязвимостей не обнаружено"
        
        return analysis

# ============================================================
# ЗАПУСК УТИЛИТ
# ============================================================

def run_nmap(target: str, context: str = "") -> Dict:
    flags = get_nmap_flags(context)
    UI.info(f"Стратегия: nmap {flags}")
    return run_command(f"nmap {flags} {target}", timeout=600)

def run_sqlmap(url: str, context: str = "") -> Dict:
    flags = get_sqlmap_flags(context)
    UI.info(f"Стратегия: sqlmap {flags}")
    return run_command(f"sqlmap -u '{url}' {flags}", timeout=1200)

def run_whatweb(target: str) -> Dict:
    return run_command(f"whatweb {target}", timeout=180)

def run_gobuster(url: str) -> Dict:
    return run_command(f"gobuster dir -u {url} -w /usr/share/wordlists/dirb/common.txt", timeout=600)

def run_nikto(target: str) -> Dict:
    return run_command(f"nikto -h {target}", timeout=900)

# ============================================================
# АДАПТИВНЫЙ ИИ-УПРАВЛЯЕМЫЙ СКАНЕР
# ============================================================

class AdaptiveScanner:
    """Умный сканер который анализирует результаты через DeepSeek и адаптируется"""
    
    def __init__(self, client, system_prompt: str):
        self.client = client
        self.system_prompt = system_prompt
        self.attempt = 0
        self.max_attempts = 3
    
    def analyze_result_with_ai(self, tool: str, output: str, target: str) -> Dict:
        """DeepSeek анализирует вывод инструмента и возвращает структурированный результат."""
        prompt = f"{tool}\n{target}\n{output[:2000]}"
        try:
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            text = response.choices[0].message.content.strip()
            match = re.search(r'\{.*\}', text, flags=re.S)
            if match:
                analysis = json.loads(match.group(0))
                if isinstance(analysis, dict):
                    analysis.setdefault("parsed", True)
                    return analysis
        except Exception as e:
            print(f"{Colors.RED}Ошибка анализа: {e}{Colors.END}")

        return {
            "success": False,
            "parsed": False,
            "found": False,
            "summary": "",
            "details": [],
            "insights": [],
            "should_retry": False,
            "user_message": "Не удалось проанализировать вывод инструмента"
        }
    
    def execute_with_adaptation(self, tool: str, target: str, initial_flags: str = "") -> Tuple[bool, str, Dict]:
        """Запустить инструмент с адаптацией к результатам"""
        
        current_flags = initial_flags
        analysis = {
            "success": False,
            "parsed": False,
            "found": False,
            "summary": "",
            "details": [],
            "insights": [],
            "should_retry": False,
            "new_flags": "",
            "next_tool": "",
            "user_message": ""
        }
        
        while self.attempt < self.max_attempts:
            self.attempt += 1
            UI.info(f"🔄 Попытка {self.attempt}/{self.max_attempts}")
            
            # Запускаем инструмент
            if tool == "nmap":
                result = run_nmap(target, current_flags)
            elif tool == "sqlmap":
                result = run_sqlmap(target, current_flags)
            elif tool == "whatweb":
                result = run_whatweb(target)
            elif tool == "gobuster":
                result = run_gobuster(target)
            elif tool == "nikto":
                result = run_nikto(target)
            else:
                return False, "Неизвестный инструмент", analysis
            
            # Анализируем результат через AI
            analysis = self.analyze_result_with_ai(tool, result["output"], target)
            
            # Выводим сообщение AI
            if analysis.get("user_message"):
                print(f"\n{Colors.CYAN}{Colors.ICON_ANALYSIS} {analysis['user_message']}{Colors.END}")
            
            # Проверяем было ли успехом
            if analysis.get("success"):
                UI.success(f"{tool.upper()} выполнен успешно")
                return True, result["output"], analysis
            
            # Если нет рекомендаций или исчерпаны попытки
            if not analysis.get("should_retry") or self.attempt >= self.max_attempts:
                if analysis.get("next_tool"):
                    UI.warning(f"Текущий инструмент не помог. Попробуем {analysis['next_tool']}")
                    return False, result["output"], analysis
                else:
                    return False, result["output"], analysis
            
            # Если нужна переб попытка с новыми флагами
            if analysis.get("new_flags"):
                current_flags = analysis["new_flags"]
                UI.info(f"Пробую с новыми флагами: {current_flags}")
                continue
            
            # Иначе выходим
            break
        
        return False, result.get("output", ""), analysis

# ============================================================
# АНАЛИЗ НАМЕРЕНИЙ
# ============================================================

class IntentAnalyzer:
    @staticmethod
    def parse_json_response(text: str) -> Dict:
        candidates = []
        try:
            candidates.append(json.loads(text))
        except Exception:
            pass

        match = re.search(r'\{.*\}', text, flags=re.S)
        if match:
            try:
                candidates.append(json.loads(match.group(0)))
            except Exception:
                pass

        for candidate in candidates:
            if isinstance(candidate, dict):
                # Гарантируем что context_keywords это строка, даже если DeepSeek вернул список
                context_keywords = candidate.get("context_keywords", "")
                if isinstance(context_keywords, list):
                    context_keywords = " ".join(str(k) for k in context_keywords)
                elif not isinstance(context_keywords, str):
                    context_keywords = str(context_keywords) if context_keywords else ""
                
                # Гарантируем что tools это список
                tools = candidate.get("tools", [])
                if isinstance(tools, str):
                    tools = [tools]
                elif not isinstance(tools, list):
                    tools = []
                
                # Гарантируем что target это строка
                target = candidate.get("target")
                if target and not isinstance(target, str):
                    target = str(target)
                
                return {
                    "intent": candidate.get("intent", "unknown"),
                    "target": target,
                    "has_params": bool(candidate.get("has_params")),
                    "tools": tools,
                    "context_keywords": context_keywords,
                    "explanation": candidate.get("explanation", "")
                }
        return {}

    @staticmethod
    def analyze(user_input: str, context_targets: List[str]) -> Dict:
        user_lower = user_input.lower()
        
        result = {
            "intent": "unknown",
            "target": None,
            "has_params": False,
            "tools": [],
            "context_keywords": "",
            "explanation": ""
        }
        
        # Извлечение цели: URL, домен, IP
        url_patterns = [
            r'https?://[^\s]+' ,
            r'\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?(?:/[^\s]*)?\b',
            r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}(?:/[^\s]*)?\b'
        ]
        urls = []
        for pattern in url_patterns:
            urls.extend(re.findall(pattern, user_input))
        urls = [u.rstrip('.,;!') for u in urls]

        if urls:
            result["target"] = urls[0]
            if not result["target"].startswith("http") and not re.match(r'\d+\.\d+\.\d+\.\d+', result["target"]):
                result["target"] = "http://" + result["target"]
            result["has_params"] = "?" in result["target"] and "=" in result["target"]
        
        # Если нет URL, но есть в контексте
        if not result["target"] and context_targets:
            context_related = any(word in user_lower for word in ['цель', 'сайт', 'admin', 'админ', 'url', 'домен', 'адрес', 'веб', 'site'])
            scan_request = any(word in user_lower for word in ['проверь', 'провер', 'скан', 'проскан', 'запусти', 'проанализируй', 'пентест', 'аудит', 'проведи', 'найди', 'ищи', 'продолжай', 'еще', 'далее'])
            if context_related or scan_request:
                result["target"] = context_targets[-1]
        
        # Если это вопрос о предыдущем результате, не запускаем новый скан.
        follow_up = any(q in user_lower for q in ['что', 'какая', 'какие', 'где', 'покажи', 'расскажи', 'итог', 'результат']) and any(t in user_lower for t in ['уязвим', 'уязвимость', 'результат', 'найден', 'обнаруж'])
        if follow_up and not any(word in user_lower for word in ['проверь', 'провер', 'скан', 'проскан', 'запусти', 'проанализируй']):
            result["intent"] = "status_query"
            result["tools"] = []
            result["explanation"] = "Запрос текущего состояния или результатов предыдущей сессии"
            return result

        # Анализ намерения
        if any(word in user_lower for word in ['sql', 'инъекц', 'sqlmap', 'проверь sql', 'найди sql', 'sql-инъекц']):
            result["intent"] = "sql_injection"
            result["tools"].append("sqlmap")
            result["explanation"] = "Проверка SQL-инъекций"
        
        elif any(word in user_lower for word in ['порты', 'nmap', 'скан портов', 'сканируй порты', 'сканер портов']):
            result["intent"] = "port_scan"
            result["tools"].append("nmap")
            result["explanation"] = "Сканирование портов"
        
        elif any(word in user_lower for word in ['директор', 'gobuster', 'скрытые пути', 'директории', 'find directories', 'список директорий']):
            result["intent"] = "directory_scan"
            result["tools"].append("gobuster")
            result["explanation"] = "Поиск директорий"
        
        elif any(word in user_lower for word in ['nikto', 'проверь сайт', 'проверь на уязвимости', 'пентест', 'аудит', 'ищи уязвимости']):
            result["intent"] = "web_vulnerability"
            result["tools"].append("nikto")
            result["explanation"] = "Проверка веб-уязимостей"
            result["tools"].append("whatweb")
            result["explanation"] = "Общее сканирование"
            if result["has_params"] and not is_admin_path(result["target"]) and not is_static_file(result["target"]):
                if any(word in user_lower for word in ['sql', 'инъекц', 'sqlmap']):
                    result["tools"].append("sqlmap")
        
        # Добавляем sqlmap, только если пользователь явно запрашивал SQL и URL подходит
        if (result["has_params"] and not is_admin_path(result["target"]) and not is_static_file(result["target"])):
            if any(word in user_lower for word in ['sql', 'инъекц', 'sqlmap', 'проверь sql', 'найди sql', 'sql-инъекц']):
                if "sqlmap" not in result["tools"]:
                    result["tools"].insert(0, "sqlmap")

        # Если цель определена, но инструмент не выбран, выберем разумное поведение
        if result["target"] and not result["tools"]:
            if re.match(r'\d{1,3}(?:\.\d{1,3}){3}', result["target"]):
                result["intent"] = "port_scan"
                result["tools"].append("nmap")
                result["explanation"] = "Сканирование портов по IP"
            else:
                result["intent"] = "general_scan"
                result["tools"].append("whatweb")
                result["explanation"] = "Общее сканирование"
        
        # Извлекаем контекстные ключевые слова для флагов
        keywords = []
        for kw in ['быстрый', 'quick', 'полный', 'full', 'агрессивный', 'aggressive', 'тихий', 'stealth', 'waf']:
            if kw in user_lower:
                keywords.append(kw)
        
        # Также извлекаем явные флаги типа --forms, --crawl и т.д.
        explicit_flags = re.findall(r'--\w+', user_input)
        if explicit_flags:
            keywords.extend(explicit_flags)
        
        result["context_keywords"] = " ".join(keywords)
        
        return result

# ============================================================
# КЛАСС СЕССИИ
# ============================================================

class Session:
    def __init__(self, target: str):
        self.id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.target = target
        self.start_time = datetime.now()
        self.results = []
        self.progress = 0
    
    def update_progress(self, current: int, total: int):
        self.progress = int(current / total * 100) if total > 0 else 0
    
    def add_result(self, tool: str, analysis: Dict, duration: float):
        self.results.append({
            "tool": tool,
            "analysis": analysis,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
    
    def save_log(self) -> str:
        """Сохранить сессию в файл"""
        try:
            log_dir = os.path.expanduser("~/.jim/sessions")
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f"{self.id}.json")
            session_data = {
                "id": self.id,
                "target": self.target,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": str(datetime.now() - self.start_time),
                "results_count": len(self.results),
                "results": self.results
            }
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            return log_file
        except Exception as e:
            print(f"{Colors.RED}Ошибка сохранения лога: {e}{Colors.END}")
            return None
    
    def print_status(self):
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}│ {Colors.ICON_TARGET} СЕССИЯ{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
        print(f"{Colors.CYAN}│ Цель:{Colors.END} {self.target[:60]}")
        print(f"{Colors.CYAN}│ Прогресс:{Colors.END}")
        UI.progress_bar(self.progress)
        print(f"{Colors.CYAN}│ Выполнено:{Colors.END} {len(self.results)}")
        print(f"{Colors.BOLD}{Colors.CYAN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    def print_report(self):
        duration = datetime.now() - self.start_time
        
        UI.header("ИТОГОВЫЙ ОТЧЁТ", Colors.ICON_REPORT)
        
        print(f"\n{Colors.CYAN}🎯 Цель:{Colors.END} {self.target}")
        print(f"{Colors.CYAN}⏱️ Длительность:{Colors.END} {str(duration).split('.')[0]}")
        
        found = [r for r in self.results if r["analysis"].get("found")]
        
        if found:
            print(f"\n{Colors.RED}{Colors.BOLD}🔴 НАЙДЕННЫЕ УЯЗВИМОСТИ:{Colors.END}")
            for r in found:
                print(f"   • {r['tool'].upper()}: {r['analysis']['summary']}")
        else:
            print(f"\n{Colors.YELLOW}⚠️ УЯЗВИМОСТЕЙ НЕ ОБНАРУЖЕНО{Colors.END}")
        
        log_file = self.save_log()
        if log_file:
            print(f"\n{Colors.GREEN}{Colors.ICON_SUCCESS} Сессия сохранена:{Colors.END}")
            print(f"{Colors.DIM}   {log_file}{Colors.END}")
        
        UI.separator("═")

# ============================================================
# ОСНОВНОЙ АГЕНТ
# ============================================================

class JimAgent:
    def __init__(self):
        self.client = None
        self.session: Optional[Session] = None
        self.context_targets: List[str] = load_context_targets()
        self.paused = False
        self.auto_mode = AUTO_MODE
    
    def initialize(self):
        import openai
        self.client = openai.OpenAI(
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.chat_history = [{"role": "system", "content": CHAT_PROMPT}]

    def ask_chat(self, user_input: str) -> str:
        if not self.client:
            return "🤖 Я пока не могу ответить на общие вопросы, задайте команду сканирования."

        try:
            self.chat_history.append({"role": "user", "content": user_input})
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-v4-flash",
                messages=self.chat_history,
                max_tokens=250,
                temperature=0.7
            )
            text = response.choices[0].message.content.strip()
            self.chat_history.append({"role": "assistant", "content": text})
            return text
        except Exception as e:
            return f"❌ Ошибка чата: {str(e)[:100]}"

    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        if not self.client:
            return IntentAnalyzer.analyze(user_input, self.context_targets)

        target_context = ""
        if self.context_targets:
            target_context = f"\nСохранённые цели из истории: {', '.join(self.context_targets[-3:])}"
        
        prompt = f"Запрос пользователя:\n{user_input}{target_context}\n"

        try:
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.0
            )
            text = response.choices[0].message.content.strip()
            parsed = IntentAnalyzer.parse_json_response(text)
            if parsed and parsed.get("tools"):
                return parsed
        except Exception:
            pass

        return IntentAnalyzer.analyze(user_input, self.context_targets)

    def process(self, user_input: str) -> str:
        if user_input.startswith('/'):
            return self._handle_command(user_input)
        
        # Команда "sqlmap" без аргументов
        if user_input.lower().strip() == "sqlmap" and self.context_targets:
            user_input = f"проверь SQL на {self.context_targets[-1]}"
            UI.info(f"Запускаю sqlmap на {self.context_targets[-1]}")
        
        UI.thinking("Анализирую ваш запрос...", 0.3)
        user_lower = user_input.lower()

        # Обработка приветов и обычных вопросов отдельно от сканирования.
        greeting_words = ['hello', 'hi', 'привет', 'здравствуйте', 'здравствуй', 'добрый', 'hey', 'yo']
        scan_triggers = ['sql', 'инъекц', 'sqlmap', 'порты', 'nmap', 'gobuster', 'nikto', 'проверь', 'скан', 'проскан', 'запусти', 'анализ', 'пентест', 'аудит', 'директ', 'сайт', 'админ']
        if any(word in user_lower for word in greeting_words) and not any(word in user_lower for word in scan_triggers):
            return self.ask_chat(user_input)

        if self.session and any(q in user_lower for q in ['что', 'какая', 'какие', 'где', 'покажи', 'расскажи', 'итог', 'результат']) and any(t in user_lower for t in ['уязвим', 'уязвимость', 'результат', 'найден', 'обнаруж']):
            self.session.print_report()
            return ""

        intent = self.analyze_intent(user_input)

        if intent.get("intent") == "status_query":
            if self.session:
                self.session.print_report()
                return ""
            return self.ask_chat(user_input)

        # Сохраняем цель
        if intent.get("target") and intent["target"] not in self.context_targets:
            self.context_targets.append(intent["target"])
            save_context_targets(self.context_targets)
        
        if not intent.get("target") or not intent.get("tools"):
            return self.ask_chat(user_input)
        
        # Создаём сессию
        self.session = Session(intent["target"])
        UI.header(intent["explanation"], Colors.ICON_ANALYSIS)
        UI.info(f"🎯 Цель: {intent['target']}")
        
        # АДАПТИВНОЕ СКАНИРОВАНИЕ С DEEPSEEK АНАЛИЗОМ
        adaptive = AdaptiveScanner(self.client, SYSTEM_PROMPT)
        tools_to_scan = list(intent["tools"])
        
        while tools_to_scan:
            tool = tools_to_scan[0]
            
            if self.paused:
                UI.warning("Сессия приостановлена. Введите /continue")
                break
            
            # Проверка для sqlmap без параметров
            if tool == "sqlmap" and not intent["has_params"]:
                UI.warning("В URL нет параметров! sqlmap может быть не эффективен.")
                if not self.auto_mode:
                    resp = input(f"{Colors.YELLOW}Продолжить? (y/n): {Colors.END}").strip().lower()
                    if resp != 'y':
                        tools_to_scan.pop(0)
                        continue
            
            UI.info(f"🔧 Запускаю {tool.upper()}...")
            
            # Запускаем с адаптацией
            success, output, ai_analysis = adaptive.execute_with_adaptation(tool, intent["target"], intent["context_keywords"])
            
            # Если DeepSeek смог разобрать вывод, используем его как первичную аналитику.
            if ai_analysis.get("parsed"):
                analysis = {
                    "found": bool(ai_analysis.get("found", False)),
                    "summary": ai_analysis.get("summary", ""),
                    "details": ai_analysis.get("details", []),
                    "insights": ai_analysis.get("insights", []),
                }
            else:
                if tool == "nmap":
                    analysis = OutputAnalyzer.analyze_nmap(output)
                elif tool == "sqlmap":
                    analysis = OutputAnalyzer.analyze_sqlmap(output)
                elif tool == "whatweb":
                    analysis = OutputAnalyzer.analyze_whatweb(output)
                elif tool == "gobuster":
                    analysis = OutputAnalyzer.analyze_gobuster(output)
                elif tool == "nikto":
                    analysis = OutputAnalyzer.analyze_nikto(output)
                else:
                    tools_to_scan.pop(0)
                    continue
            
            self.session.add_result(tool, analysis, 0)
            
            # Вывод анализа
            print(f"\n{Colors.BOLD}{Colors.CYAN}{'─' * 70}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}📊 АНАЛИЗ {tool.upper()}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}{'─' * 70}{Colors.END}")
            
            if analysis.get("found"):
                print(f"{Colors.GREEN}{analysis['summary']}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}{analysis['summary']}{Colors.END}")
            
            for insight in analysis.get("insights", [])[:3]:
                print(f"   {insight}")
            for detail in analysis.get("details", [])[:5]:
                print(f"   • {detail}")
            
            # Критическая находка - остановка
            if success and analysis.get("found"):
                UI.success("🎯 УЯЗВИМОСТЬ НАЙДЕНА!")
                if tool == "sqlmap":
                    UI.warning("🚨 КРИТИЧЕСКАЯ! SQL-инъекция подтверждена!")
                    break
            
            tools_to_scan.pop(0)
            adaptive.attempt = 0  # Сброс для следующего инструмента
        
        self.session.print_report()
        
        return "✅ Готово"
    
    def _handle_command(self, command: str) -> str:
        cmd = command.lower().strip('/')
        
        if cmd in ["status", "stats"]:
            if self.session:
                self.session.print_status()
                return ""
            return "📊 Нет активной сессии"
        
        elif cmd in ["stop", "pause"]:
            self.paused = True
            return "⏸️ Сессия приостановлена. Введите /continue для продолжения"
        
        elif cmd in ["continue", "resume"]:
            self.paused = False
            return "▶️ Сессия возобновлена"
        
        elif cmd in ["report", "summary"]:
            if self.session:
                self.session.print_report()
                return ""
            return "📊 Нет отчёта"
        
        elif cmd in ["save", "savelog"]:
            if self.session:
                log_file = self.session.save_log()
                if log_file:
                    return f"{Colors.ICON_SUCCESS} Сессия сохранена: {log_file}"
                return f"{Colors.ICON_ERROR} Ошибка сохранения"
            return "📊 Нет активной сессии для сохранения"
        
        elif cmd in ["context", "targets"]:
            if self.context_targets:
                result = "📋 СОХРАНЁННЫЕ ЦЕЛИ:\n"
                for i, t in enumerate(self.context_targets, 1):
                    result += f"   {i}. {t}\n"
                return result
            return "📋 Нет сохранённых целей"
        
        elif cmd in ["reset", "clear"]:
            self.context_targets = []
            save_context_targets(self.context_targets)
            self.session = None
            self.paused = False
            return f"{Colors.ICON_RESET} Память очищена"
        
        elif cmd in ["help", "?"]:
            return """
╔════════════════════════════════════════════════════════════════════╗
║                         JIM - ПОМОЩЬ                               ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  🔍 SQL ИНЪЕКЦИИ:                                                 ║
║     • "проверь site.com/page?id=1 на SQL"                         ║
║     • "sqlmap" (использует последнюю цель)                        ║
║                                                                    ║
║  🔌 ПОРТЫ:                                                        ║
║     • "найди открытые порты на 192.168.1.1"                       ║
║     • "быстрое сканирование портов"                               ║
║                                                                    ║
║  📁 ДИРЕКТОРИИ:                                                   ║
║     • "найди скрытые директории на example.com"                   ║
║                                                                    ║
║  🌐 ВЕБ УЯЗВИМОСТИ:                                               ║
║     • "проверь сайт на уязвимости"                                ║
║                                                                    ║
║  ⚙️ КОМАНДЫ:                                                      ║
║     • /status - статус сессии                                     ║
║     • /stop - остановить сканирование                             ║
║     • /continue - продолжить                                      ║
║     • /report - итоговый отчёт                                    ║
║     • /save - сохранить логи сессии                               ║
║     • /context - показать цели                                    ║
║     • /reset - очистить память                                    ║
║     • /exit - выход                                               ║
║                                                                    ║
║  ⌨️ ГОРЯЧИЕ КЛАВИШИ:                                              ║
║     • Ctrl+C - остановить текущее сканирование                    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝"""
        
        return f"❌ Неизвестно: {command}. Введите /help"

# ============================================================
# ЗАПУСК
# ============================================================

def print_banner():
    os.system('clear')
    banner = """
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                              ║
║    ██╗ ██╗███╗   ███╗         █████╗ ██╗███████╗███╗   ██╗████████╗                        ║
║    ██║ ██║████╗ ████║        ██╔══██╗██║██╔════╝████╗  ██║╚══██╔══╝                        ║
║    ██║ ██║██╔████╔██║        ███████║██║█████╗  ██╔██╗ ██║   ██║                           ║
║    ██║ ██║██║╚██╔╝██║        ██╔══██║██║██╔══╝  ██║╚██╗██║   ██║                           ║
║    ███████║██║ ╚═╝ ██║██╗     ██║  ██║██║███████╗██║ ╚████║   ██║                           ║
║    ╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝                           ║
║                                                                                              ║
║                         █████╗ ██╗       ███████╗███╗   ██╗████████╗                         ║
║                        ██╔══██╗██║       ██╔════╝████╗  ██║╚══██╔══╝                         ║
║                        ███████║██║       █████╗  ██╔██╗ ██║   ██║                            ║
║                        ██╔══██║██║       ██╔══╝  ██║╚██╗██║   ██║                            ║
║                        ██║  ██║███████╗  ███████╗██║ ╚████║   ██║                            ║
║                        ╚═╝  ╚═╝╚══════╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝                            ║
║                                                                                              ║
║                         🤖 JIM - ИНТЕЛЛЕКТУАЛЬНЫЙ ИИ-АГЕНТ 🤖                                ║
║                      Понимаю естественный язык | Полный анализ | Сохранение сессий          ║
║                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
"""
    print(f"{Colors.CYAN}{banner}{Colors.END}")
    print(f"{Colors.DIM}{'='*70}{Colors.END}")

def main():
    global session_start_time
    
    print_banner()
    
    if not check_api_key():
        sys.exit(1)
    
    agent = JimAgent()
    agent.initialize()
    
    print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}JIM ГОТОВ{Colors.END} | {Colors.ICON_SHIELD} Понимаю естественный язык")
    print(f"{Colors.ICON_INFO} Просто опишите, что нужно сделать")
    print(f"{Colors.DIM}{'='*70}{Colors.END}")
    print(f"{Colors.DIM}Подсказка: /help для справки, Ctrl+C для остановки сканирования{Colors.END}\n")
    
    main_start_time = time.time()
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}[{Colors.ICON_USER}]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', 'exit', 'quit']:
                elapsed = int(time.time() - main_start_time)
                if agent.context_targets:
                    print(f"\n{Colors.CYAN}📋 Сеансов проведено: {len(agent.context_targets)}{Colors.END}")
                print(f"{Colors.CYAN}⏱️  Время работы: {elapsed}с{Colors.END}")
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
                session_start_time = None
                break
            
            if not user_input:
                continue
            
            response = agent.process(user_input)
            if response:
                print(f"\n{Colors.ICON_AGENT} {response}")
            
        except KeyboardInterrupt:
            if session_start_time:
                elapsed = int(time.time() - session_start_time)
                print(f"\n\n{Colors.BOLD}{Colors.YELLOW}⏸️  Сканирование остановлено ({elapsed}с){Colors.END}")
            print(f"{Colors.DIM}Введите /exit для выхода или команду для продолжения{Colors.END}")
            session_start_time = None
            continue
        except Exception as e:
            print(f"\n{Colors.ICON_ERROR} {Colors.RED}Ошибка: {str(e)[:100]}{Colors.END}")
            session_start_time = None
            continue

if __name__ == "__main__":
    main()