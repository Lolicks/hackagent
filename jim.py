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
║    status, stop, report, save, history, reset, help               ║
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
# АНАЛИЗ ЦЕЛИ
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
        
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ip_matches = re.findall(ip_pattern, user_input)
        if ip_matches:
            result["target_type"] = "ip"
            result["target"] = ip_matches[0]
            result["explanation"] = f"Обнаружен IP-адрес: {ip_matches[0]}"
            result["suggested_tools"] = ["nmap"]
        
        url_pattern = r'https?://[^\s]+|[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}[^\s]*'
        url_matches = re.findall(url_pattern, user_input)
        if url_matches:
            url = url_matches[0]
            if not url.startswith("http"):
                url = "http://" + url
            result["target_type"] = "url"
            result["target"] = url
            result["has_parameters"] = "?" in url and "=" in url
            result["explanation"] = f"Обнаружен URL: {url}"
            result["suggested_tools"] = ["whatweb"]
            if result["has_parameters"]:
                result["suggested_tools"].insert(0, "sqlmap")
                result["explanation"] += " | Обнаружены параметры → приоритет SQL-инъекциям"
        
        keywords = ["sql", "инъекц", "injection", "директори", "directory", 
                    "порт", "port", "уязвим", "vulnerab", "скан", "scan", 
                    "быстрый", "quick", "полный", "full", "агрессивный", "aggressive"]
        for kw in keywords:
            if kw in user_input.lower():
                result["keywords"].append(kw)
        
        if "sql" in result["keywords"] or "инъекц" in result["keywords"]:
            if "sqlmap" not in result["suggested_tools"]:
                result["suggested_tools"].insert(0, "sqlmap")
        
        return result

# ============================================================
# АНАЛИЗ ВЫВОДА (ИСПРАВЛЕННАЯ ВЕРСИЯ)
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
            if "filtered" in output.lower():
                analysis["insights"].append("🛡️ Порт фильтруется - возможно активен фаервол")
        
        return analysis
    
    @staticmethod
    def analyze_sqlmap(output: str) -> Dict[str, Any]:
        """Анализирует вывод sqlmap - корректно определяет наличие инъекции"""
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        output_lower = output.lower()
        
        # Индикаторы ОТСУТСТВИЯ уязвимости
        not_found_indicators = [
            "does not appear to be injectable",
            "all tested parameters do not appear to be injectable",
            "not vulnerable",
            "no injection",
            "no parameter found",
            "no parameter seems to be injectable"
        ]
        
        # Индикаторы НАЛИЧИЯ уязвимости
        found_indicators = [
            "parameter .* is vulnerable",
            "vulnerable to sql injection",
            "the back-end dbms is",
            "sql injection found",
            "injectable parameter",
            "fetching database",
            "current database:"
        ]
        
        # Сначала проверяем что уязвимость НЕ найдена
        is_not_found = any(re.search(pattern, output_lower) for pattern in not_found_indicators)
        
        if is_not_found:
            analysis["found"] = False
            analysis["summary"] = "🛡️ SQL-инъекция НЕ обнаружена"
            
            if "waf" in output_lower or "ips" in output_lower:
                analysis["insights"].append("🛡️ Обнаружена WAF/IPS защита")
            if "403" in output or "forbidden" in output_lower:
                analysis["insights"].append("🚫 Сервер вернул 403 Forbidden - доступ ограничен")
            if "429" in output or "too many requests" in output_lower:
                analysis["insights"].append("⚠️ Обнаружено ограничение запросов (429)")
            if "no get parameter" in output_lower:
                analysis["insights"].append("❓ В URL нет параметров для проверки")
            
            return analysis
        
        # Проверяем на наличие уязвимости
        is_found = any(re.search(pattern, output_lower) for pattern in found_indicators)
        
        if is_found:
            analysis["found"] = True
            analysis["summary"] = "🐛 SQL-инъекция ОБНАРУЖЕНА!"
            
            if "boolean" in output_lower and "blind" in output_lower:
                analysis["details"].append("Тип: Boolean-based Blind SQLi")
                analysis["insights"].append("🎯 Boolean-based: Можно извлекать данные побитово")
            if "union" in output_lower:
                analysis["details"].append("Тип: Union-based SQLi")
                analysis["insights"].append("🎯 Union-based: Быстрое извлечение данных")
            if "time" in output_lower and "blind" in output_lower:
                analysis["details"].append("Тип: Time-based Blind SQLi")
                analysis["insights"].append("🎯 Time-based: Работает даже без видимого вывода")
            if "error" in output_lower:
                analysis["details"].append("Тип: Error-based SQLi")
                analysis["insights"].append("🎯 Error-based: Утечка данных через ошибки БД")
            
            # Поиск баз данных
            dbs = re.findall(r'\[\*\*\]\s+(\w+)', output)
            if not dbs:
                dbs = re.findall(r'\[\[\s*\]\]\s+(\w+)', output)
            if dbs:
                system_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']
                user_dbs = [db for db in dbs if db not in system_dbs]
                if user_dbs:
                    analysis["details"].append(f"Найдены базы данных: {', '.join(user_dbs[:5])}")
                    analysis["insights"].append(f"📊 Обнаружено {len(user_dbs)} пользовательских БД")
            
            # Поиск текущего пользователя
            user_match = re.search(r'current user:\s*[\'"]?(\w+)[\'"]?', output_lower)
            if user_match:
                analysis["insights"].append(f"👤 Пользователь БД: {user_match.group(1)}")
        else:
            analysis["found"] = False
            analysis["summary"] = "🛡️ SQL-инъекция НЕ обнаружена"
            
            if "waf" in output_lower:
                analysis["insights"].append("🛡️ Обнаружена WAF защита")
            if "429" in output:
                analysis["insights"].append("⚠️ Активно ограничение запросов")
        
        return analysis
    
    @staticmethod
    def analyze_gobuster(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        dirs = re.findall(r'/(\S+)\s+\(Status:\s+(\d+)\)', output)
        interesting = [d for d in dirs if d[1] in ["200", "301", "302", "401", "403", "500"]]
        
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
                    analysis["insights"].append(f"🚫 Запрещено, но существует: /{path}")
                elif status == "500":
                    analysis["insights"].append(f"⚠️ Ошибка на: /{path} (возможна уязвимость)")
        else:
            analysis["summary"] = "📭 Интересных директорий не найдено"
        
        return analysis
    
    @staticmethod
    def analyze_nikto(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        vuln_pattern = r'\+ (.*?):'
        all_vulns = re.findall(vuln_pattern, output)
        critical_keywords = ['cve', 'vulnerable', 'rce', 'remote', 'execution', 'injection', 'sql', 'xss', 'csrf']
        critical = [v for v in all_vulns if any(k in v.lower() for k in critical_keywords)]
        
        if critical:
            analysis["found"] = True
            analysis["summary"] = f"⚠️ Обнаружено {len(critical)} потенциальных уязвимостей"
            for v in critical[:10]:
                analysis["details"].append(v[:80])
                if 'cve' in v.lower():
                    analysis["insights"].append(f"🔴 Известная CVE: {v[:60]}")
                if 'xss' in v.lower():
                    analysis["insights"].append("💉 Обнаружена XSS уязвимость")
        
        server_match = re.search(r'\+ Server:\s*(.+?)(?:\n|$)', output, re.IGNORECASE)
        if server_match:
            analysis["insights"].append(f"🖥️ Сервер: {server_match.group(1).strip()}")
        
        if not analysis["found"]:
            analysis["summary"] = "🛡️ Очевидных уязвимостей не обнаружено"
        
        return analysis
    
    @staticmethod
    def analyze_whatweb(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        # Очищаем вывод от мусорных символов
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        
        # Ищем технологии в квадратных скобках
        techs = re.findall(r'\[(.*?)\]', clean_output)
        clean_techs = []
        for t in techs:
            t_clean = t.strip()
            # Фильтруем мусор
            if (len(t_clean) < 50 and 
                'http' not in t_clean.lower() and 
                'm' not in t_clean and
                '[' not in t_clean and
                ']' not in t_clean and
                t_clean not in clean_techs):
                clean_techs.append(t_clean)
        
        # Также ищем прямые упоминания технологий
        direct_techs = re.findall(r'(Apache|nginx|IIS|PHP|Python|Ruby|Node\.js|WordPress|Joomla|Drupal|Magento)', clean_output, re.IGNORECASE)
        for tech in direct_techs:
            if tech not in clean_techs:
                clean_techs.append(tech)
        
        if clean_techs:
            analysis["found"] = True
            analysis["summary"] = f"🔧 Обнаружено {len(clean_techs)} технологий"
            for t in clean_techs[:15]:
                analysis["details"].append(t)
            
            cms_list = ['WordPress', 'Joomla', 'Drupal', 'Magento']
            for tech in clean_techs:
                if tech in cms_list:
                    analysis["insights"].append(f"📰 Обнаружена CMS: {tech}")
                elif 'nginx' in tech.lower():
                    analysis["insights"].append("⚡ Обнаружен Nginx")
                elif 'apache' in tech.lower():
                    analysis["insights"].append("🔄 Обнаружен Apache")
                elif 'php' in tech.lower():
                    analysis["insights"].append("🐘 Обнаружен PHP")
        else:
            analysis["summary"] = "❓ Технологии не определены"
            ip_match = re.search(r'IP\[([0-9.]+)\]', clean_output)
            if ip_match:
                analysis["insights"].append(f"🌐 IP сервера: {ip_match.group(1)}")
        
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
                    if 'vulnerable' in line.lower() or 'injectable' in line.lower():
                        print(f"{Colors.BG_RED}{Colors.BOLD}{Colors.WHITE}{line.rstrip()}{Colors.END}")
                    elif 'open' in line.lower() and 'tcp' in line.lower():
                        print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                    elif 'error' in line.lower():
                        print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                    elif 'database' in line.lower():
                        print(f"{Colors.CYAN}{line.rstrip()}{Colors.END}")
                    elif 'found' in line.lower() or 'discovered' in line.lower():
                        print(f"{Colors.YELLOW}{line.rstrip()}{Colors.END}")
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
        self.current_process = None
        
        self.session_dir = os.path.expanduser(f"~/.jim/sessions/{self.session_id}")
        os.makedirs(self.session_dir, exist_ok=True)
    
    def add_result(self, result: ScanResult):
        self.scan_history.append(result)
        self._extract_findings(result)
        self._update_progress()
        self._save_session()
    
    def _extract_findings(self, result: ScanResult):
        if result.tool == "nmap":
            ports = re.findall(r'(\d+)/tcp\s+open', result.output)
            self.discovered_ports = list(set(self.discovered_ports + [int(p) for p in ports]))
            if any(p in self.discovered_ports for p in [80, 443, 8080]):
                self.found_vulnerabilities.append({
                    "severity": "info",
                    "type": "web_service",
                    "description": "Обнаружен веб-сервис",
                    "timestamp": result.timestamp
                })
        elif result.tool == "sqlmap" and result.analysis.get("found"):
            self.found_vulnerabilities.append({
                "severity": "critical",
                "type": "sql_injection",
                "description": result.analysis.get("summary", "Обнаружена SQL-инъекция"),
                "details": result.analysis.get("details", []),
                "timestamp": result.timestamp
            })
        elif result.tool == "whatweb" and result.analysis.get("found"):
            self.technologies = result.analysis.get("details", [])
        elif result.tool == "nikto" and result.analysis.get("found"):
            for vuln in result.analysis.get("details", [])[:5]:
                severity = "high" if "cve" in vuln.lower() else "medium"
                self.found_vulnerabilities.append({
                    "severity": severity,
                    "type": "web_vulnerability",
                    "description": vuln[:100],
                    "timestamp": result.timestamp
                })
    
    def _update_progress(self):
        self.progress = min(100, len(self.scan_history) * 12)
    
    def _save_session(self):
        session_data = {
            "session_id": self.session_id,
            "target": self.target,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "discovered_ports": self.discovered_ports,
            "technologies": self.technologies,
            "found_vulnerabilities": self.found_vulnerabilities,
            "scan_history": [
                {
                    "tool": r.tool,
                    "status": r.status.value,
                    "duration": r.duration,
                    "analysis": r.analysis
                }
                for r in self.scan_history
            ]
        }
        save_path = os.path.join(self.session_dir, "session.json")
        with open(save_path, 'w') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def print_status(self):
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}│ {Colors.ICON_TARGET} СТАТУС СЕССИИ{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
        print(f"{Colors.CYAN}│ Сессия:{Colors.END} {self.session_id}")
        print(f"{Colors.CYAN}│ Цель:{Colors.END} {Colors.BOLD}{self.target}{Colors.END}")
        print(f"{Colors.CYAN}│ Фаза:{Colors.END} {self.current_phase}")
        print(f"{Colors.CYAN}│ Прогресс:{Colors.END}")
        UI.progress_bar(int(self.progress))
        print(f"{Colors.CYAN}│ Запущено утилит:{Colors.END} {len(self.scan_history)}")
        print(f"{Colors.CYAN}│ Найдено уязвимостей:{Colors.END} {len(self.found_vulnerabilities)}")
        print(f"{Colors.CYAN}│ Длительность:{Colors.END} {str(datetime.now() - self.start_time).split('.')[0]}")
        if self.found_vulnerabilities:
            print(f"{Colors.CYAN}│ Находки:{Colors.END}")
            for vuln in self.found_vulnerabilities[:3]:
                severity_color = Colors.RED if vuln["severity"] == "critical" else Colors.YELLOW
                print(f"{Colors.DIM}│   {severity_color}▪ {vuln['description'][:50]}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    def print_final_report(self):
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{Colors.ICON_REPORT} ИТОГОВЫЙ ОТЧЁТ{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")
        print(f"\n{Colors.CYAN}🎯 Цель:{Colors.END} {Colors.BOLD}{self.target}{Colors.END}")
        print(f"{Colors.CYAN}⏱️ Длительность:{Colors.END} {str(duration).split('.')[0]}")
        print(f"{Colors.CYAN}🛠️ Использовано утилит:{Colors.END} {len(self.scan_history)}")
        
        critical = [v for v in self.found_vulnerabilities if v["severity"] == "critical"]
        high = [v for v in self.found_vulnerabilities if v["severity"] == "high"]
        medium = [v for v in self.found_vulnerabilities if v["severity"] == "medium"]
        
        if critical:
            print(f"\n{Colors.BG_RED}{Colors.BOLD}{Colors.WHITE}🔴 КРИТИЧЕСКИЕ УЯЗВИМОСТИ{Colors.END}")
            for v in critical:
                print(f"   • {v['description']}")
        if high:
            print(f"\n{Colors.RED}{Colors.BOLD}🟠 ВЫСОКИЙ РИСК{Colors.END}")
            for v in high:
                print(f"   • {v['description']}")
        if medium:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}🟡 СРЕДНИЙ РИСК{Colors.END}")
            for v in medium:
                print(f"   • {v['description']}")
        
        if self.technologies:
            print(f"\n{Colors.CYAN}{Colors.BOLD}🔧 ОБНАРУЖЕННЫЕ ТЕХНОЛОГИИ{Colors.END}")
            for tech in self.technologies[:10]:
                print(f"   • {tech}")
        
        if self.discovered_ports:
            print(f"\n{Colors.CYAN}{Colors.BOLD}🔌 ОТКРЫТЫЕ ПОРТЫ{Colors.END}")
            print(f"   {', '.join(map(str, self.discovered_ports[:15]))}")
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}💡 РЕКОМЕНДАЦИИ{Colors.END}")
        if critical:
            print(f"   • Немедленно исправьте критические уязвимости")
        if any('sql' in str(v).lower() for v in critical):
            print(f"   • Используйте параметризованные запросы для защиты от SQL-инъекций")
        if 'WordPress' in self.technologies:
            print(f"   • Запустите wpscan для поиска уязвимостей WordPress")
        if not self.found_vulnerabilities:
            print(f"   • Очевидных уязвимостей не найдено. Рекомендуется ручное тестирование.")
        
        print(f"\n{Colors.DIM}📁 Сессия сохранена: ~/.jim/sessions/{self.session_id}/{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")

# ============================================================
# ОСНОВНОЙ АГЕНТ
# ============================================================

class JimAgent:
    def __init__(self):
        if not API_KEY:
            UI.error("API ключ не найден!")
            UI.info("Запустите ./install.sh для настройки")
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
    
    def process(self, user_input: str) -> str:
        if user_input.startswith('/'):
            return self._handle_command(user_input)
        
        UI.loading_animation("Анализ цели...", 0.3)
        analysis = TargetAnalyzer.analyze(user_input)
        
        if not analysis["target"]:
            return "❌ Не удалось определить цель. Укажите IP-адрес или URL."
        
        self.session = JimSession(analysis["target"])
        self.session.current_phase = "Анализ цели"
        self.session.print_status()
        
        return self._execute_plan(analysis)
    
    def _execute_plan(self, analysis: Dict) -> str:
        target = analysis["target"]
        suggested_tools = analysis["suggested_tools"]
        
        if self.dry_run:
            return self._dry_run_report(analysis)
        
        results = []
        
        for tool in suggested_tools:
            if self.session.paused:
                UI.warning("Сессия приостановлена. Введите 'continue' для продолжения")
                break
            
            self.session.current_phase = f"Запуск {tool}"
            self.session.print_status()
            
            if not self.auto_mode:
                print(f"\n{Colors.YELLOW}📋 Следующий шаг: {tool.upper()} на {target}{Colors.END}")
                response = input(f"{Colors.CYAN}Запустить? (y/n/skip/auto): {Colors.END}").strip().lower()
                if response == 'n':
                    UI.info("Пропускаем...")
                    continue
                elif response == 'auto':
                    self.auto_mode = True
                elif response == 'skip':
                    UI.info("Пропускаем...")
                    continue
            
            result = self._run_tool(tool, target, analysis.get("keywords", []))
            
            if result and result.get("interrupted"):
                UI.warning("Сканирование прервано пользователем")
                break
            
            if result:
                analysis_result = self._analyze_tool_output(tool, result.get("output", ""))
                scan_result = ScanResult(
                    tool=tool,
                    status=ScanStatus.COMPLETED if result.get("success") else ScanStatus.FAILED,
                    command="",
                    output=result.get("output", "")[:5000],
                    analysis=analysis_result,
                    duration=result.get("duration", 0),
                    timestamp=datetime.now().isoformat()
                )
                self.session.add_result(scan_result)
                self._print_analysis(tool, analysis_result)
                
                if analysis_result.get("found") and tool == "sqlmap":
                    UI.warning("КРИТИЧЕСКО: Обнаружена SQL-инъекция! Дальнейшее сканирование остановлено.")
                    break
        
        self.session.print_final_report()
        return "✅ Оценка завершена"
    
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
        return {"success": False, "error": f"Неизвестный инструмент: {tool}"}
    
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
        return {"found": False, "summary": "Неизвестный инструмент", "details": [], "insights": []}
    
    def _print_analysis(self, tool: str, analysis: Dict):
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}│ {Colors.ICON_ANALYSIS} АНАЛИЗ - {tool.upper()}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
        
        if analysis.get("found"):
            print(f"{Colors.DIM}│{Colors.END} {Colors.RED}{analysis.get('summary', 'Найдено')}{Colors.END}")
        else:
            print(f"{Colors.DIM}│{Colors.END} {Colors.GREEN}{analysis.get('summary', 'Не найдено')}{Colors.END}")
        
        for insight in analysis.get("insights", [])[:5]:
            print(f"{Colors.DIM}│{Colors.END}   {insight}")
        for detail in analysis.get("details", [])[:5]:
            print(f"{Colors.DIM}│{Colors.END}   • {detail}")
        
        print(f"{Colors.BOLD}{Colors.CYAN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    def _dry_run_report(self, analysis: Dict) -> str:
        target = analysis["target"]
        suggested_tools = analysis["suggested_tools"]
        report = f"""
{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}
{Colors.BOLD}{Colors.CYAN}{Colors.ICON_SPARKLES} РЕЖИМ DRY RUN - Что будет выполнено{Colors.END}
{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}

🎯 Цель: {target}
📋 Тип: {analysis['target_type']}
🔍 Ключевые слова: {', '.join(analysis['keywords']) if analysis['keywords'] else 'нет'}

📊 План сканирования:
"""
        for i, tool in enumerate(suggested_tools, 1):
            flags, explanation = self._get_default_flags(tool, target)
            report += f"""
{i}. {tool.upper()}
   → Флаги: {flags}
   → Зачем: {explanation}
"""
        report += f"""
{Colors.YELLOW}ℹ️ Реальное сканирование не выполнялось. Запустите без --dry-run для выполнения.{Colors.END}
{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}
"""
        return report
    
    def _get_default_flags(self, tool: str, target: str) -> Tuple[str, str]:
        if tool == "nmap":
            return get_nmap_flags(target, "", self.profile)
        elif tool == "sqlmap":
            return get_sqlmap_flags(target, "", self.profile)
        elif tool == "gobuster":
            return get_gobuster_flags(target, "", self.profile)
        elif tool == "nikto":
            return get_nikto_flags(target, "", self.profile)
        elif tool == "whatweb":
            return get_whatweb_flags(target, "", self.profile)
        return ("", "")
    
    def _handle_command(self, command: str) -> str:
        cmd = command.lower().strip('/')
        
        if cmd in ["status", "stats"]:
            if self.session:
                self.session.print_status()
                return ""
            return "ℹ️ Нет активной сессии. Укажите цель (IP или URL)."
        
        elif cmd in ["stop", "pause"]:
            if self.session:
                self.session.paused = True
                return "⏸️ Сессия приостановлена. Введите 'continue' для продолжения"
            return "ℹ️ Нет активной сессии для приостановки"
        
        elif cmd in ["continue", "resume"]:
            if self.session:
                self.session.paused = False
                return "▶️ Сессия возобновлена"
            return "ℹ️ Нет активной сессии для возобновления"
        
        elif cmd in ["report", "summary"]:
            if self.session:
                self.session.print_final_report()
                return ""
            return "ℹ️ Нет активной сессии. Сначала начните сканирование."
        
        elif cmd in ["save", "export"]:
            if self.session:
                self.session._save_session()
                return f"💾 Сессия сохранена в ~/.jim/sessions/{self.session.session_id}/"
            return "ℹ️ Нет активной сессии для сохранения"
        
        elif cmd in ["history", "log"]:
            if self.session:
                if not self.session.scan_history:
                    return "📋 В этой сессии ещё не было сканирований"
                print(f"\n{Colors.BOLD}📋 История сканирований:{Colors.END}")
                for i, scan in enumerate(self.session.scan_history, 1):
                    status_icon = Colors.ICON_SUCCESS if scan.status == ScanStatus.COMPLETED else Colors.ICON_ERROR
                    status_color = Colors.GREEN if scan.status == ScanStatus.COMPLETED else Colors.RED
                    print(f"  {i}. {status_icon} {status_color}{scan.tool.upper()}{Colors.END} - {scan.duration:.1f}с")
                    if scan.analysis.get("summary"):
                        print(f"     └─ {scan.analysis['summary'][:60]}")
                return ""
            return "ℹ️ Нет истории сессии"
        
        elif cmd in ["reset", "clear_memory", "forget", "clear"]:
            # Очищаем историю сообщений
            self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            # Очищаем текущую сессию
            if self.session:
                self.session = None
            # Сбрасываем глобальное состояние
            global interrupted, current_process
            interrupted = False
            if current_process:
                try:
                    current_process.terminate()
                    current_process = None
                except:
                    pass
            # Очищаем экран если указано
            if 'screen' in command.lower() or 'cls' in command.lower():
                os.system('clear')
                print_banner()
            
            return f"""
{Colors.BOLD}{Colors.CYAN}╔════════════════════════════════════════════════════════════════════╗{Colors.END}
{Colors.BOLD}{Colors.CYAN}║                    {Colors.ICON_RESET} ПАМЯТЬ ОЧИЩЕНА {Colors.ICON_RESET}                     ║{Colors.END}
{Colors.BOLD}{Colors.CYAN}╠════════════════════════════════════════════════════════════════════╣{Colors.END}
{Colors.BOLD}{Colors.CYAN}║                                                                    ║{Colors.END}
{Colors.BOLD}{Colors.CYAN}║  {Colors.GREEN}✅{Colors.END} История диалога очищена                                    ║{Colors.END}
{Colors.BOLD}{Colors.CYAN}║  {Colors.GREEN}✅{Colors.END} Контекст сессии очищен                                      ║{Colors.END}
{Colors.BOLD}{Colors.CYAN}║  {Colors.GREEN}✅{Colors.END} Активные сканирования остановлены                            ║{Colors.END}
{Colors.BOLD}{Colors.CYAN}║  {Colors.GREEN}✅{Colors.END} Память агента сброшена к заводским настройкам                ║{Colors.END}
{Colors.BOLD}{Colors.CYAN}║                                                                    ║{Colors.END}
{Colors.BOLD}{Colors.CYAN}║  {Colors.ICON_INFO} Jim готов к новым целям!                                   ║{Colors.END}
{Colors.BOLD}{Colors.CYAN}║                                                                    ║{Colors.END}
{Colors.BOLD}{Colors.CYAN}╚════════════════════════════════════════════════════════════════════╝{Colors.END}"""
        
        elif cmd in ["help", "?"]:
            return """
╔════════════════════════════════════════════════════════════════════╗
║                      ИНТЕРАКТИВНЫЕ КОМАНДЫ                         ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  УПРАВЛЕНИЕ СЕССИЕЙ:                                              ║
║    /status, /stats   - Показать статус текущей сессии             ║
║    /stop, /pause     - Приостановить сканирование                 ║
║    /continue, /resume- Возобновить сканирование                   ║
║    /reset, /clear    - Очистить ВСЮ память и контекст             ║
║    /reset screen     - Очистить память И экран                    ║
║                                                                    ║
║  ОТЧЁТЫ:                                                          ║
║    /report, /summary - Показать итоговый отчёт                    ║
║    /save, /export    - Сохранить текущую сессию                   ║
║    /history, /log    - Показать историю сканирований              ║
║                                                                    ║
║  ПРОЧЕЕ:                                                          ║
║    /help, /?         - Показать эту справку                       ║
║    /exit, /quit      - Выйти из Jim                               ║
║                                                                    ║
║  💡 Примеры:                                                      ║
║    > Проверь сайт example.com на уязвимости                       ║
║    > Агрессивное сканирование nmap на 192.168.1.1                ║
║    > Проверь SQL на site.com/page?id=1                           ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝"""
        
        return f"❌ Неизвестная команда: {command}. Введите /help для списка команд"

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
    print(f"{Colors.ICON_ROCKET} {Colors.GREEN}Jim инициализирован{Colors.END} | {Colors.ICON_SHIELD} Готов к работе")
    print(f"{Colors.ICON_INFO} Команды: {Colors.YELLOW}/help{Colors.END} | {Colors.YELLOW}/status{Colors.END} | {Colors.YELLOW}/reset{Colors.END} | {Colors.YELLOW}/exit{Colors.END}")
    print(f"{Colors.ICON_FLAG} Профиль: {Colors.BOLD}{PROFILE}{Colors.END} | Режим: {Colors.BOLD}{'Авто' if AUTO_MODE else 'Интерактивный'}{Colors.END}")
    print(f"{Colors.DIM}{'='*70}{Colors.END}")

def main():
    print_banner()
    agent = JimAgent()
    
    if AUTO_MODE and len(sys.argv) > 2:
        target = ' '.join(sys.argv[2:])
        print(f"\n{Colors.ICON_AGENT} {Colors.BLUE}Автономный режим: сканирование {target}{Colors.END}")
        response = agent.process(target)
        print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}Готово!{Colors.END}")
        return
    
    print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}Интерактивный режим. Введите цель или /help{Colors.END}")
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}[{Colors.ICON_USER} jim]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
                break
            
            if not user_input:
                continue
            
            response = agent.process(user_input)
            if response:
                print(f"\n{Colors.ICON_AGENT} {response}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} {Colors.YELLOW}Прервано. Введите /exit для выхода{Colors.END}")
            continue
        except EOFError:
            print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
            break

if __name__ == "__main__":
    main()