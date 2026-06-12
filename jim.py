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
║                         🤖 JIM - AI АССИСТЕНТ ДЛЯ ПЕНТЕСТА 🤖                                 ║
║                                   v2.0.0 | Умный агент                                        ║
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
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================
# ОБРАБОТКА СИГНАЛОВ
# ============================================================

current_process = None
interrupted = False

def signal_handler(sig, frame):
    global interrupted, current_process
    interrupted = True
    if current_process:
        try:
            current_process.terminate()
        except:
            pass

signal.signal(signal.SIGINT, signal_handler)

# ============================================================
# ВЕРСИЯ И АРГУМЕНТЫ
# ============================================================

VERSION = "2.0.0"

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
        print(" 📦 Загрузка репозитория...")
        subprocess.run(["git", "clone", "--depth", "1", repo_url, temp_dir], check=True, capture_output=True)
        print(" 📄 Обновление файлов...")
        shutil.copy2(f"{temp_dir}/jim.py", f"{jim_dir}/jim.py")
        shutil.copy2(f"{temp_dir}/system_prompt.txt", f"{jim_dir}/")
        shutil.rmtree(temp_dir)
        print("\n ✅ Обновление завершено успешно!")
        return True
    except Exception as e:
        print(f" ❌ Ошибка обновления: {e}")
        return False

# Обработка аргументов командной строки
AUTO_MODE = False
DRY_RUN = False
PROFILE = "normal"

args = sys.argv[1:]
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
║  Использование:                                                    ║
║    jim                              → Интерактивный режим          ║
║    jim -a, --auto "цель"            → Автономный режим             ║
║    jim --dry-run "цель"             → Показать план без выполнения ║
║    jim --profile stealth|aggressive → Выбрать профиль              ║
║    jim -h, --help                   → Показать справку             ║
║    jim -v, --version                → Показать версию              ║
║    jim -u, --update                 → Обновить из GitHub           ║
║                                                                    ║
║  Интерактивные команды:                                            ║
║    /status, /stats   - статус сессии                               ║
║    /stop, /pause     - приостановить                               ║
║    /continue, /resume- возобновить                                 ║
║    /report, /summary - итоговый отчёт                              ║
║    /save, /export    - сохранить сессию                            ║
║    /history, /log    - история сканирований                        ║
║    /context, /targets- показать сохранённые цели                   ║
║    /reset, /clear    - очистить память                             ║
║    /help, /?         - справка                                     ║
║    /exit, /quit      - выход                                       ║
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
# ПРЕМИУМ ЦВЕТОВАЯ СХЕМА
# ============================================================

class Colors:
    BLACK = '\033[30m'
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
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    END = '\033[0m'
    
    BG_BLACK = '\033[40m'
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    BG_PURPLE = '\033[105m'
    BG_CYAN = '\033[106m'
    
    ICON_AGENT = "🤖"
    ICON_USER = "👤"
    ICON_TOOL = "⚙️"
    ICON_ANALYSIS = "🔍"
    ICON_DECISION = "🎯"
    ICON_REPORT = "📊"
    ICON_INFO = "ℹ️"
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"
    ICON_FLAG = "🚩"
    ICON_CLOCK = "⏱️"
    ICON_TARGET = "🎯"
    ICON_BUG = "🐛"
    ICON_SHIELD = "🛡️"
    ICON_NETWORK = "🌐"
    ICON_DATABASE = "💾"
    ICON_TABLE = "📋"
    ICON_FOLDER = "📁"
    ICON_ROCKET = "🚀"
    ICON_SPARKLES = "✨"
    ICON_PAUSE = "⏸️"
    ICON_PLAY = "▶️"
    ICON_STOP = "⏹️"
    ICON_RESET = "🧹"

# ============================================================
# СТРУКТУРЫ ДАННЫХ
# ============================================================

class ScanStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ScanResult:
    tool: str
    status: ScanStatus
    command: str
    output: str
    analysis: Dict[str, Any]
    duration: float
    timestamp: str

@dataclass
class Session:
    session_id: str
    target: str
    start_time: str
    end_time: Optional[str]
    scan_history: List[ScanResult]
    discovered_ports: List[int]
    technologies: List[str]
    found_vulnerabilities: List[Dict]
    current_phase: str
    progress: float
    context: Dict[str, Any]

# ============================================================
# UI КОМПОНЕНТЫ
# ============================================================

class UI:
    @staticmethod
    def separator(char: str = "─", length: int = 70, color: str = Colors.DIM):
        print(f"{color}{char * length}{Colors.END}")
    
    @staticmethod
    def header(text: str, icon: str = "⚡", color: str = Colors.CYAN):
        print(f"\n{color}{Colors.BOLD}{icon} {text}{Colors.END}")
        UI.separator("─", 70, Colors.DIM)
    
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
    def progress_bar(percent: int, width: int = 40):
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        color = Colors.GREEN if percent < 70 else Colors.YELLOW if percent < 90 else Colors.RED
        print(f"{color}{bar}{Colors.END} {percent}%")
    
    @staticmethod
    def loading_animation(text: str, duration: float = 0.5):
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            sys.stdout.write(f"\r{Colors.CYAN}{chars[i % len(chars)]} {text}{Colors.END}")
            sys.stdout.flush()
            time.sleep(0.05)
            i += 1
        sys.stdout.write("\r" + " " * (len(text) + 5) + "\r")

# ============================================================
# ЗАГРУЗКА НАСТРОЕК
# ============================================================

def load_api_key():
    env_path = os.path.expanduser("~/.jim/.env")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None

def load_system_prompt():
    if os.path.exists("system_prompt.txt"):
        with open("system_prompt.txt", 'r', encoding='utf-8') as f:
            return f.read()
    prompt_path = os.path.expanduser("~/.jim/system_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    return """Ты - Jim, умный помощник для пентеста. Будь полезным."""

def ensure_directories():
    dirs = [
        os.path.expanduser("~/.jim"),
        os.path.expanduser("~/.jim/sessions"),
        os.path.expanduser("~/.jim/reports"),
        os.path.expanduser("~/.jim/logs"),
        os.path.expanduser("~/.jim/cache"),
        os.path.expanduser("~/.jim/wordlists")
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

API_KEY = load_api_key()
SYSTEM_PROMPT = load_system_prompt()
ensure_directories()

# ============================================================
# УМНЫЙ ВЫБОР ФЛАГОВ
# ============================================================

def get_nmap_flags(target: str, context: str = "", profile: str = "normal") -> Tuple[str, str]:
    flags = "-sV --open"
    explanation = "Стандартное сканирование портов с определением версий"
    
    if "все порты" in context.lower() or "full" in context.lower():
        flags = "-sV -p- --open --min-rate=1000"
        explanation = "Полное сканирование всех портов (1-65535)"
    elif "быстрый" in context.lower() or "quick" in context.lower():
        flags = "-F --open"
        explanation = "Быстрое сканирование (только топ-100 портов)"
    elif "агрессивный" in context.lower() or "aggressive" in context.lower():
        flags = "-sV -sC -O --open --version-intensity=9"
        explanation = "Агрессивное сканирование: версии, скрипты, ОС"
    elif "udp" in context.lower():
        flags = "-sU --open"
        explanation = "Сканирование UDP портов"
    elif profile == "stealth":
        flags = "-sS -Pn -T2 -f --data-length=200 --randomize-hosts --spoof-mac 0"
        explanation = "Скрытый режим: SYN-сканирование, без пинга, фрагментация"
    elif profile == "aggressive":
        flags = "-sV -sC -O -A -T4 -p-"
        explanation = "Максимально агрессивный профиль"
    
    return flags, explanation

def get_sqlmap_flags(url: str, context: str = "", profile: str = "normal") -> Tuple[str, str]:
    flags = "--batch --dbs --level=1"
    explanation = "Стандартная проверка SQL-инъекций, перечисление БД"
    
    if "полный" in context.lower() or "full" in context.lower():
        flags = "--batch --dbs --tables --level=3 --risk=2"
        explanation = "Полное сканирование: базы данных, таблицы, колонки"
    elif "быстрый" in context.lower() or "quick" in context.lower():
        flags = "--batch --current-db --level=1"
        explanation = "Быстрая проверка: только текущая БД"
    elif "os-shell" in context.lower():
        flags = "--batch --os-shell"
        explanation = "ОПАСНО: попытка получить доступ к ОС"
    elif "waf" in context.lower():
        flags = "--batch --dbs --level=3 --risk=2 --random-agent --tamper=space2comment,charencode"
        explanation = "Режим обхода WAF"
    elif profile == "stealth":
        flags = "--batch --dbs --level=1 --delay=5 --random-agent --tor --check-tor"
        explanation = "Скрытый режим: задержки, Tor"
    elif profile == "aggressive":
        flags = "--batch --dbs --tables --level=5 --risk=3 --threads=10"
        explanation = "Агрессивный режим: высокий уровень/риск"
    
    return flags, explanation

def get_gobuster_flags(url: str, context: str = "", profile: str = "normal") -> Tuple[str, str]:
    wordlist = "/usr/share/wordlists/dirb/common.txt"
    flags = f"dir -u {url} -w {wordlist}"
    explanation = "Перебор директорий со стандартным словарём"
    
    if "большой" in context.lower() or "big" in context.lower():
        wordlist = "/usr/share/wordlists/dirb/big.txt"
        flags = f"dir -u {url} -w {wordlist}"
        explanation = "Режим большого словаря (big.txt)"
    elif "расширение" in context.lower() or "extension" in context.lower():
        flags = f"dir -u {url} -w {wordlist} -x php,txt,html,asp,aspx,js,css,json,xml,bak,old,sql"
        explanation = "Поиск с расширениями файлов"
    elif profile == "stealth":
        flags = f"dir -u {url} -w {wordlist} -t 10 --delay 2"
        explanation = "Скрытый режим: медленные запросы"
    elif profile == "aggressive":
        flags = f"dir -u {url} -w {wordlist} -t 50"
        explanation = "Агрессивный режим: много потоков"
    
    return flags, explanation

def get_nikto_flags(target: str, context: str = "", profile: str = "normal") -> Tuple[str, str]:
    flags = f"-h {target}"
    explanation = "Стандартное сканирование веб-уязвимостей"
    
    if "ssl" in context.lower() or "https" in context.lower():
        flags = f"-h {target} -ssl"
        explanation = "Режим SSL/HTTPS"
    elif "агрессивный" in context.lower() or "aggressive" in context.lower():
        flags = f"-h {target} -maxtime=600 -Tuning=4"
        explanation = "Агрессивное сканирование"
    elif profile == "stealth":
        flags = f"-h {target} -delay 5 -nossl"
        explanation = "Скрытый режим: задержки между запросами"
    
    return flags, explanation

def get_whatweb_flags(target: str, context: str = "", profile: str = "normal") -> Tuple[str, str]:
    flags = target
    explanation = "Базовое определение технологий"
    
    if "подробный" in context.lower() or "verbose" in context.lower():
        flags = f"-v {target}"
        explanation = "Подробный вывод"
    elif "агрессивный" in context.lower() or "aggressive" in context.lower():
        flags = f"-a 3 {target}"
        explanation = "Агрессивный режим (больше плагинов)"
    elif profile == "stealth":
        flags = f"-a 1 {target}"
        explanation = "Скрытый режим (лёгкий набор плагинов)"
    
    return flags, explanation

# ============================================================
# АНАЛИЗ ЦЕЛИ (ИСПРАВЛЕННАЯ ВЕРСИЯ)
# ============================================================

class TargetAnalyzer:
    @staticmethod
    def analyze(user_input: str) -> Dict[str, Any]:
        result = {
            "raw_input": user_input,
            "target_type": "unknown",
            "target": None,
            "has_parameters": False,
            "keywords": [],
            "suggested_tools": [],
            "explanation": ""
        }
        
        user_lower = user_input.lower()
        
        # Извлекаем ключевые слова
        wants_sql = any(word in user_lower for word in ['sqlmap', 'sql инъекц', 'инъекц', 'sql', 'уязвим', 'проверь sql'])
        wants_ports = any(word in user_lower for word in ['nmap', 'порты', 'порт', 'скан портов'])
        wants_dirs = any(word in user_lower for word in ['gobuster', 'директор', 'скрытые пути', 'брутфорс'])
        wants_web_vulns = any(word in user_lower for word in ['nikto', 'веб уязвим', 'сайт на уязвим'])
        
        def clean_url(url: str) -> str:
            url = url.rstrip('.').strip()
            if not url.startswith("http"):
                url = "http://" + url
            url = re.sub(r'#.*$', '', url)
            return url
        
        # Поиск IP
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ip_matches = re.findall(ip_pattern, user_input)
        valid_ips = []
        for ip in ip_matches:
            if not re.search(r'/\d+\.\d+\.\d+\.\d+/', user_input) and len(ip) < 20:
                valid_ips.append(ip)
        
        if valid_ips:
            result["target_type"] = "ip"
            result["target"] = valid_ips[0]
            result["explanation"] = f"Обнаружен IP-адрес: {valid_ips[0]}"
            result["suggested_tools"] = ["nmap"]
            if wants_web_vulns:
                result["suggested_tools"].append("nikto")
        
        # Поиск URL
        url_pattern = r'https?://[^\s]+|[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}(?:/\S*)?'
        raw_urls = re.findall(url_pattern, user_input)
        
        valid_urls = []
        for url in raw_urls:
            if re.search(r'\.php(?:\(\d+\))?:\d+', url):
                continue
            if len(url) > 150:
                continue
            if 'mysql' in url.lower() or ('sql' in url.lower() and 'error' in user_lower):
                continue
            valid_urls.append(clean_url(url))
        
        if valid_urls:
            url = valid_urls[0]
            result["target_type"] = "url"
            result["target"] = url
            result["has_parameters"] = "?" in url and "=" in url
            
            # КЛЮЧЕВОЕ РЕШЕНИЕ: когда запускать sqlmap
            should_run_sqlmap = False
            
            if result["has_parameters"]:
                should_run_sqlmap = True
                result["explanation"] = "Обнаружены параметры в URL → проверка SQL-инъекций"
            elif wants_sql:
                should_run_sqlmap = True
                result["explanation"] = "Пользователь хочет проверить SQL → запуск sqlmap"
            elif 'sql' in user_lower and ('error' in user_lower or 'exception' in user_lower):
                should_run_sqlmap = True
                result["explanation"] = "Обнаружена SQL ошибка → нужно проверить"
            
            if should_run_sqlmap:
                result["suggested_tools"].append("sqlmap")
                result["suggested_tools"].append("whatweb")
            else:
                result["suggested_tools"].append("whatweb")
                if wants_dirs:
                    result["suggested_tools"].append("gobuster")
                if wants_web_vulns:
                    result["suggested_tools"].append("nikto")
            
            if wants_ports:
                result["suggested_tools"].insert(0, "nmap")
        
        if not result["target"]:
            if wants_sql:
                result["explanation"] = "Укажите URL с параметрами (например, site.com/page?id=1)"
            elif wants_ports:
                result["explanation"] = "Укажите IP-адрес или домен"
        
        result["suggested_tools"] = list(dict.fromkeys(result["suggested_tools"]))
        
        # Отладка
        print(f"{Colors.DIM}[DEBUG] Target: {result['target']}{Colors.END}")
        print(f"{Colors.DIM}[DEBUG] Has params: {result['has_parameters']}{Colors.END}")
        print(f"{Colors.DIM}[DEBUG] Tools: {result['suggested_tools']}{Colors.END}")
        
        return result

# ============================================================
# АНАЛИЗ ВЫВОДА
# ============================================================

class OutputAnalyzer:
    @staticmethod
    def analyze_nmap(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        open_ports = re.findall(r'(\d+)/tcp\s+open\s+(\w+)', output)
        if open_ports:
            analysis["found"] = True
            analysis["summary"] = f"🔓 Обнаружено {len(open_ports)} открытых портов"
            for port, service in open_ports[:10]:
                analysis["details"].append(f"Порт {port}: {service}")
                if port in ["80", "443", "8080", "8443"]:
                    analysis["insights"].append(f"🌐 Веб-сервер на порту {port}")
                elif service in ["mysql", "postgresql", "mongodb", "redis"]:
                    analysis["insights"].append(f"🗄️ База данных ({service}) на порту {port}")
        else:
            analysis["summary"] = "🔒 Открытых портов не найдено"
        
        return analysis
    
    @staticmethod
    def analyze_sqlmap(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        output_lower = output.lower()
        
        not_found_indicators = [
            "does not appear to be injectable",
            "all tested parameters do not appear to be injectable",
            "not vulnerable",
            "no injection",
            "no parameter found"
        ]
        
        found_indicators = [
            "parameter .* is vulnerable",
            "vulnerable to sql injection",
            "the back-end dbms is",
            "sql injection found",
            "injectable parameter"
        ]
        
        is_not_found = any(re.search(pattern, output_lower) for pattern in not_found_indicators)
        
        if is_not_found:
            analysis["found"] = False
            analysis["summary"] = "🛡️ SQL-инъекция НЕ обнаружена"
            if "waf" in output_lower:
                analysis["insights"].append("🛡️ Обнаружена WAF/IPS защита")
            if "403" in output:
                analysis["insights"].append("🚫 Доступ ограничен (403)")
            return analysis
        
        is_found = any(re.search(pattern, output_lower) for pattern in found_indicators)
        
        if is_found:
            analysis["found"] = True
            analysis["summary"] = "🐛 SQL-инъекция ОБНАРУЖЕНА!"
            
            if "boolean" in output_lower:
                analysis["details"].append("Тип: Boolean-based Blind SQLi")
            if "union" in output_lower:
                analysis["details"].append("Тип: Union-based SQLi")
            if "time" in output_lower:
                analysis["details"].append("Тип: Time-based Blind SQLi")
            
            dbs = re.findall(r'\[\*\*\]\s+(\w+)', output)
            if dbs:
                analysis["details"].append(f"Базы данных: {', '.join(dbs[:5])}")
        else:
            analysis["found"] = False
            analysis["summary"] = "🛡️ SQL-инъекция НЕ обнаружена"
        
        return analysis
    
    @staticmethod
    def analyze_gobuster(output: str) -> Dict[str, Any]:
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
                elif status == "401":
                    analysis["insights"].append(f"🔒 Требуется авторизация: /{path}")
                elif status == "403":
                    analysis["insights"].append(f"🚫 Запрещено: /{path}")
        else:
            analysis["summary"] = "📭 Интересных директорий не найдено"
        
        return analysis
    
    @staticmethod
    def analyze_nikto(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        vuln_pattern = r'\+ (.*?):'
        all_vulns = re.findall(vuln_pattern, output)
        critical = [v for v in all_vulns if any(k in v.lower() for k in ['cve', 'vulnerable', 'xss', 'sql'])]
        
        if critical:
            analysis["found"] = True
            analysis["summary"] = f"⚠️ Обнаружено {len(critical)} потенциальных уязвимостей"
            for v in critical[:10]:
                analysis["details"].append(v[:80])
        
        if not analysis["found"]:
            analysis["summary"] = "🛡️ Очевидных уязвимостей не обнаружено"
        
        return analysis
    
    @staticmethod
    def analyze_whatweb(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        
        ignore_words = [
            '429', 'Too Many Requests', 'hcdn', 'cloudflare', 'ddos',
            '403', '404', '500', 'Forbidden', 'GERMANY', 'DE', 'USA',
            'HTTPServer', 'UncommonHeaders', 'RedirectLocation', 'Title'
        ]
        
        real_techs = ['Apache', 'nginx', 'IIS', 'PHP', 'Python', 'Ruby', 'Node.js',
                      'WordPress', 'Joomla', 'Drupal', 'Magento', 'MySQL', 'PostgreSQL']
        
        techs = re.findall(r'\[(.*?)\]', clean_output)
        clean_techs = []
        
        for t in techs:
            t_clean = t.strip()
            if any(ignore.lower() in t_clean.lower() for ignore in ignore_words):
                continue
            if (2 < len(t_clean) < 50 and not t_clean.isdigit() and t_clean not in clean_techs):
                clean_techs.append(t_clean)
        
        for tech in real_techs:
            if tech.lower() in clean_output.lower() and tech not in clean_techs:
                clean_techs.append(tech)
        
        ip_match = re.search(r'IP\[([0-9.]+)\]', clean_output)
        
        if clean_techs:
            analysis["found"] = True
            analysis["summary"] = f"🔧 Обнаружено {len(clean_techs)} технологий"
            for t in clean_techs[:8]:
                analysis["details"].append(t)
        elif ip_match:
            analysis["summary"] = "🌐 Технологии не определены"
            analysis["insights"].append(f"💡 IP: {ip_match.group(1)}")
        else:
            analysis["summary"] = "❓ Технологии не определены"
        
        return analysis

# ============================================================
# ЗАПУСК УТИЛИТ
# ============================================================

def run_command(cmd: str, timeout: int = 300, show_output: bool = True) -> Dict:
    global current_process, interrupted
    
    if show_output:
        print(f"{Colors.DIM}└─$ {cmd}{Colors.END}")
        UI.separator("─", 70, Colors.DIM)
    
    interrupted = False
    output_lines = []
    start_time = time.time()
    
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
                current_process.terminate()
                print(f"\n{Colors.ICON_WARNING} {Colors.YELLOW}Прервано пользователем{Colors.END}")
                return {"success": False, "output": "\n".join(output_lines), "interrupted": True}
            
            if line:
                output_lines.append(line.rstrip())
                if show_output:
                    if 'vulnerable' in line.lower():
                        print(f"{Colors.BG_RED}{Colors.BOLD}{Colors.WHITE}{line.rstrip()}{Colors.END}")
                    elif 'open' in line.lower() and 'tcp' in line.lower():
                        print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                    elif 'error' in line.lower():
                        print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                    else:
                        print(f"{Colors.DIM}{line.rstrip()}{Colors.END}")
        
        current_process.wait(timeout=timeout)
        duration = time.time() - start_time
        
        return {
            "success": current_process.returncode == 0,
            "output": "\n".join(output_lines),
            "duration": duration,
            "interrupted": False
        }
    except subprocess.TimeoutExpired:
        current_process.terminate()
        return {"success": False, "output": "\n".join(output_lines), "error": "Timeout", "duration": timeout}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e), "duration": 0}
    finally:
        current_process = None

def run_nmap(target: str, flags: str = None, context: str = "", profile: str = "normal") -> Dict:
    if flags is None:
        flags, explanation = get_nmap_flags(target, context, profile)
        UI.info(f"Стратегия: {explanation}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} NMAP СКАНИРОВАНИЕ{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.CYAN}│ Цель:{Colors.END} {Colors.BOLD}{target}{Colors.END}")
    print(f"{Colors.CYAN}│ Флаги:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    cmd = f"nmap {flags} {target}"
    return run_command(cmd, timeout=600)

def run_sqlmap(url: str, flags: str = None, context: str = "", profile: str = "normal") -> Dict:
    if flags is None:
        flags, explanation = get_sqlmap_flags(url, context, profile)
        UI.info(f"Стратегия: {explanation}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} SQLMAP СКАНИРОВАНИЕ{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.CYAN}│ Цель:{Colors.END} {Colors.BOLD}{url}{Colors.END}")
    print(f"{Colors.CYAN}│ Флаги:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    cmd = f"sqlmap -u '{url}' {flags}"
    return run_command(cmd, timeout=1200)

def run_gobuster(url: str, flags: str = None, context: str = "", profile: str = "normal") -> Dict:
    if flags is None:
        flags, explanation = get_gobuster_flags(url, context, profile)
        UI.info(f"Стратегия: {explanation}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} GOBUSTER СКАНИРОВАНИЕ{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.CYAN}│ Цель:{Colors.END} {Colors.BOLD}{url}{Colors.END}")
    print(f"{Colors.CYAN}│ Флаги:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    cmd = f"gobuster {flags}"
    return run_command(cmd, timeout=600)

def run_nikto(target: str, flags: str = None, context: str = "", profile: str = "normal") -> Dict:
    if flags is None:
        flags, explanation = get_nikto_flags(target, context, profile)
        UI.info(f"Стратегия: {explanation}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} NIKTO СКАНИРОВАНИЕ{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.CYAN}│ Цель:{Colors.END} {Colors.BOLD}{target}{Colors.END}")
    print(f"{Colors.CYAN}│ Флаги:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    cmd = f"nikto {flags}"
    return run_command(cmd, timeout=900)

def run_whatweb(target: str, flags: str = None, context: str = "", profile: str = "normal") -> Dict:
    if flags is None:
        flags, explanation = get_whatweb_flags(target, context, profile)
        UI.info(f"Стратегия: {explanation}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} WHATWEB СКАНИРОВАНИЕ{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.CYAN}│ Цель:{Colors.END} {Colors.BOLD}{target}{Colors.END}")
    print(f"{Colors.CYAN}│ Флаги:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    cmd = f"whatweb {flags}"
    return run_command(cmd, timeout=180)

# ============================================================
# КЛАСС СЕССИИ
# ============================================================

class JimSession:
    def __init__(self, target: str):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.target = target
        self.start_time = datetime.now()
        self.end_time = None
        self.scan_history: List[ScanResult] = []
        self.discovered_ports: List[int] = []
        self.technologies: List[str] = []
        self.found_vulnerabilities: List[Dict] = []
        self.current_phase = "Инициализация"
        self.progress = 0
        self.context = {}
        self.paused = False
        
        self.session_dir = os.path.expanduser(f"~/.jim/sessions/{self.session_id}")
        os.makedirs(self.session_dir, exist_ok=True)
    
    def add_result(self, result: ScanResult):
        self.scan_history.append(result)
        self._extract_findings(result)
        self._update_progress()
        self._save_session()
    
    def _extract_findings(self, result: ScanResult):
        if result.tool == "sqlmap" and result.analysis.get("found"):
            self.found_vulnerabilities.append({
                "severity": "critical",
                "type": "sql_injection",
                "description": result.analysis.get("summary", "SQL-инъекция"),
                "timestamp": result.timestamp
            })
        elif result.tool == "whatweb" and result.analysis.get("found"):
            self.technologies = result.analysis.get("details", [])
    
    def _update_progress(self):
        self.progress = min(100, len(self.scan_history) * 20)
    
    def _save_session(self):
        session_data = {
            "session_id": self.session_id,
            "target": self.target,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "technologies": self.technologies,
            "found_vulnerabilities": self.found_vulnerabilities,
            "scan_history": [{"tool": r.tool, "duration": r.duration} for r in self.scan_history]
        }
        save_path = os.path.join(self.session_dir, "session.json")
        with open(save_path, 'w') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def print_status(self):
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}│ {Colors.ICON_TARGET} СТАТУС СЕССИИ{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
        print(f"{Colors.CYAN}│ Цель:{Colors.END} {Colors.BOLD}{self.target[:60]}{Colors.END}")
        print(f"{Colors.CYAN}│ Фаза:{Colors.END} {self.current_phase}")
        print(f"{Colors.CYAN}│ Прогресс:{Colors.END}")
        UI.progress_bar(int(self.progress))
        print(f"{Colors.CYAN}│ Выполнено:{Colors.END} {len(self.scan_history)}")
        print(f"{Colors.CYAN}│ Найдено:{Colors.END} {len(self.found_vulnerabilities)}")
        print(f"{Colors.BOLD}{Colors.CYAN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    def print_final_report(self):
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{Colors.ICON_REPORT} ИТОГОВЫЙ ОТЧЁТ{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")
        print(f"\n{Colors.CYAN}🎯 Цель:{Colors.END} {self.target}")
        print(f"{Colors.CYAN}⏱️ Длительность:{Colors.END} {str(duration).split('.')[0]}")
        
        critical = [v for v in self.found_vulnerabilities if v["severity"] == "critical"]
        if critical:
            print(f"\n{Colors.BG_RED}{Colors.BOLD}{Colors.WHITE}🔴 КРИТИЧЕСКИЕ УЯЗВИМОСТИ{Colors.END}")
            for v in critical:
                print(f"   • {v['description']}")
        
        if self.technologies:
            print(f"\n{Colors.CYAN}{Colors.BOLD}🔧 ТЕХНОЛОГИИ{Colors.END}")
            for tech in self.technologies[:8]:
                print(f"   • {tech}")
        
        if not self.found_vulnerabilities:
            print(f"\n{Colors.YELLOW}⚠️ Уязвимостей не обнаружено{Colors.END}")
        
        print(f"\n{Colors.DIM}📁 Сессия: ~/.jim/sessions/{self.session_id}/{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")

# ============================================================
# ОСНОВНОЙ АГЕНТ
# ============================================================

class JimAgent:
    def __init__(self):
        if not API_KEY:
            UI.error("API ключ не найден!")
            UI.info("Запустите ./install.sh")
            sys.exit(1)
        
        import openai
        self.client = openai.OpenAI(
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.session: Optional[JimSession] = None
        self.profile = PROFILE
        self.dry_run = DRY_RUN
        self.auto_mode = AUTO_MODE
        self.context_targets = []
    
    def process(self, user_input: str) -> str:
        if user_input.startswith('/'):
            return self._handle_command(user_input)
        
        # Сохраняем URL из запроса
        url_pattern = r'https?://[^\s]+|[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}(?:/\S*)?'
        found_urls = re.findall(url_pattern, user_input)
        for url in found_urls:
            if len(url) < 100 and url not in self.context_targets:
                clean_url = url.rstrip('.').strip()
                if not clean_url.startswith("http"):
                    clean_url = "http://" + clean_url
                self.context_targets.append(clean_url)
        
        UI.loading_animation("Анализ цели...", 0.3)
        analysis = TargetAnalyzer.analyze(user_input)
        
        if not analysis["target"]:
            if self.context_targets:
                UI.info(f"Сохранённые цели: {', '.join(self.context_targets[:3])}")
                return "❌ Укажите цель (IP или URL с параметрами для SQL)"
            return "❌ Укажите IP-адрес или URL"
        
        self.session = JimSession(analysis["target"])
        self.session.current_phase = "Анализ"
        self.session.print_status()
        
        return self._execute_plan(analysis)
    
    def _execute_plan(self, analysis: Dict) -> str:
        target = analysis["target"]
        suggested_tools = analysis["suggested_tools"].copy()
        
        # Дополнительная проверка для sqlmap
        if "sqlmap" in suggested_tools:
            skip_sqlmap = False
            target_lower = target.lower()
            
            if not analysis["has_parameters"]:
                skip_sqlmap = True
                UI.info("В URL нет параметров → sqlmap не нужен")
            elif any(x in target_lower for x in ['/admin', '/login', '/wp-admin', '/dashboard']):
                skip_sqlmap = True
                UI.info("Это страница авторизации → sqlmap не эффективен")
            
            if skip_sqlmap:
                suggested_tools.remove("sqlmap")
                if "whatweb" not in suggested_tools:
                    suggested_tools.insert(0, "whatweb")
        
        if self.dry_run:
            return self._dry_run_report(analysis)
        
        for tool in suggested_tools:
            if self.session.paused:
                UI.warning("Сессия приостановлена")
                break
            
            self.session.current_phase = f"Запуск {tool}"
            self.session.print_status()
            
            if not self.auto_mode:
                print(f"\n{Colors.YELLOW}📋 Запустить {tool.upper()}?{Colors.END}")
                resp = input(f"{Colors.CYAN}(y/n/skip/auto): {Colors.END}").strip().lower()
                if resp in ['n', 'skip']:
                    UI.info("Пропускаем")
                    continue
                elif resp == 'auto':
                    self.auto_mode = True
            
            result = self._run_tool(tool, target, analysis.get("keywords", []))
            
            if result and result.get("interrupted"):
                break
            
            if result:
                analysis_res = self._analyze_tool_output(tool, result.get("output", ""))
                scan_res = ScanResult(
                    tool=tool,
                    status=ScanStatus.COMPLETED if result.get("success") else ScanStatus.FAILED,
                    command="",
                    output=result.get("output", "")[:3000],
                    analysis=analysis_res,
                    duration=result.get("duration", 0),
                    timestamp=datetime.now().isoformat()
                )
                self.session.add_result(scan_res)
                self._print_analysis(tool, analysis_res)
                
                if analysis_res.get("found") and tool == "sqlmap":
                    UI.warning("КРИТИЧЕСКАЯ УЯЗВИМОСТЬ! Сканирование остановлено")
                    break
        
        self.session.print_final_report()
        
        if len(self.context_targets) > 1:
            UI.info(f"Другие цели: /context")
        
        return "✅ Готово"
    
    def _run_tool(self, tool: str, target: str, keywords: List[str]) -> Dict:
        context = " ".join(keywords)
        if tool == "nmap":
            return run_nmap(target, context=context, profile=self.profile)
        elif tool == "sqlmap":
            return run_sqlmap(target, context=context, profile=self.profile)
        elif tool == "gobuster":
            return run_gobuster(target, context=context, profile=self.profile)
        elif tool == "nikto":
            return run_nikto(target, context=context, profile=self.profile)
        elif tool == "whatweb":
            return run_whatweb(target, context=context, profile=self.profile)
        return {"success": False, "error": f"Неизвестный {tool}"}
    
    def _analyze_tool_output(self, tool: str, output: str) -> Dict:
        if tool == "nmap":
            return OutputAnalyzer.analyze_nmap(output)
        elif tool == "sqlmap":
            return OutputAnalyzer.analyze_sqlmap(output)
        elif tool == "gobuster":
            return OutputAnalyzer.analyze_gobuster(output)
        elif tool == "nikto":
            return OutputAnalyzer.analyze_nikto(output)
        elif tool == "whatweb":
            return OutputAnalyzer.analyze_whatweb(output)
        return {"found": False, "summary": "Анализ не выполнен"}
    
    def _print_analysis(self, tool: str, analysis: Dict):
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}│ {Colors.ICON_ANALYSIS} {tool.upper()}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
        
        if analysis.get("found"):
            print(f"{Colors.DIM}│{Colors.END} {Colors.RED}{analysis.get('summary', 'Найдено')}{Colors.END}")
        else:
            print(f"{Colors.DIM}│{Colors.END} {Colors.GREEN}{analysis.get('summary', 'Не найдено')}{Colors.END}")
        
        for insight in analysis.get("insights", [])[:3]:
            print(f"{Colors.DIM}│{Colors.END}   {insight}")
        for detail in analysis.get("details", [])[:5]:
            print(f"{Colors.DIM}│{Colors.END}   • {detail}")
        
        print(f"{Colors.BOLD}{Colors.CYAN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    def _dry_run_report(self, analysis: Dict) -> str:
        return "\n".join([
            f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}",
            f"{Colors.BOLD}{Colors.CYAN}🎯 DRY RUN - План действий{Colors.END}",
            f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}",
            f"\n🎯 Цель: {analysis['target']}",
            f"📋 Тип: {analysis['target_type']}",
            f"🔧 Инструменты: {', '.join(analysis['suggested_tools'])}",
            f"\n{Colors.YELLOW}ℹ️ Реальное сканирование не выполнялось{Colors.END}",
            f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}"
        ])
    
    def _handle_command(self, command: str) -> str:
        cmd = command.lower().strip('/')
        
        if cmd in ["status", "stats"]:
            if self.session:
                self.session.print_status()
                return ""
            return "ℹ️ Нет активной сессии"
        
        elif cmd in ["stop", "pause"]:
            if self.session:
                self.session.paused = True
                return "⏸️ Сессия приостановлена"
            return "ℹ️ Нет сессии"
        
        elif cmd in ["continue", "resume"]:
            if self.session:
                self.session.paused = False
                return "▶️ Сессия возобновлена"
            return "ℹ️ Нет сессии"
        
        elif cmd in ["report", "summary"]:
            if self.session:
                self.session.print_final_report()
                return ""
            return "ℹ️ Нет сессии"
        
        elif cmd in ["save", "export"]:
            if self.session:
                self.session._save_session()
                return f"💾 Сохранено в ~/.jim/sessions/{self.session.session_id}/"
            return "ℹ️ Нет сессии"
        
        elif cmd in ["context", "targets"]:
            if self.context_targets:
                print(f"\n{Colors.BOLD}📋 Сохранённые цели:{Colors.END}")
                for i, t in enumerate(self.context_targets, 1):
                    print(f"  {i}. {t}")
                return ""
            return "ℹ️ Нет сохранённых целей"
        
        elif cmd in ["reset", "clear"]:
            self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            self.session = None
            self.context_targets = []
            global interrupted, current_process
            interrupted = False
            if current_process:
                try:
                    current_process.terminate()
                except:
                    pass
            return f"{Colors.ICON_RESET} Память очищена"
        
        elif cmd in ["help", "?"]:
            return """
╔════════════════════════════════════════════════════════════════════╗
║                         ИНТЕРАКТИВНЫЕ КОМАНДЫ                      ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  /status   - статус сессии                                        ║
║  /stop     - приостановить                                        ║
║  /continue - возобновить                                          ║
║  /report   - итоговый отчёт                                       ║
║  /save     - сохранить сессию                                     ║
║  /context  - показать цели                                        ║
║  /reset    - очистить память                                      ║
║  /help     - справка                                              ║
║  /exit     - выход                                                ║
║                                                                    ║
║  💡 Примеры:                                                      ║
║    > проверь SQL на site.com/page?id=1                           ║
║    > просканируй site.com                                         ║
║    > nmap на 192.168.1.1                                          ║
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
║                         🤖 JIM - AI АССИСТЕНТ ДЛЯ ПЕНТЕСТА 🤖                                 ║
║                                   v2.0.0 | Умный агент                                        ║
║                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
"""
    print(f"{Colors.CYAN}{banner}{Colors.END}")
    print(f"{Colors.DIM}{'='*70}{Colors.END}")
    print(f"{Colors.ICON_ROCKET} {Colors.GREEN}Jim готов{Colors.END} | {Colors.ICON_SHIELD} Умный агент")
    print(f"{Colors.ICON_INFO} /help | /status | /context | /exit")
    print(f"{Colors.DIM}{'='*70}{Colors.END}")

def main():
    print_banner()
    agent = JimAgent()
    
    if AUTO_MODE and len(sys.argv) > 2:
        target = ' '.join(sys.argv[2:])
        print(f"\n{Colors.ICON_AGENT} Автономный режим: {target}")
        agent.process(target)
        return
    
    print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}Интерактивный режим{Colors.END}")
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}[{Colors.ICON_USER} jim]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', 'exit', 'quit']:
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
                break
            
            if not user_input:
                continue
            
            response = agent.process(user_input)
            if response:
                print(f"\n{Colors.ICON_AGENT} {response}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} Прервано. /exit для выхода")
            continue

if __name__ == "__main__":
    main()