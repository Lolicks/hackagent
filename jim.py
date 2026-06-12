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
    env_path = os.path.expanduser("~/.jim/.env")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None

def load_system_prompt():
    prompt_path = os.path.expanduser("~/.jim/system_prompt.txt")
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

API_KEY = load_api_key()
SYSTEM_PROMPT = load_system_prompt()
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
        return True
    except Exception as e:
        UI.error(f"Ошибка подключения: {str(e)[:50]}")
        return False

# ============================================================
# УМНЫЙ ВЫБОР ФЛАГОВ
# ============================================================

def get_nmap_flags(context: str) -> str:
    if "быстрый" in context or "quick" in context:
        return "-F --open"
    elif "все порты" in context or "full" in context:
        return "-p- --open"
    elif "агрессивный" in context or "aggressive" in context:
        return "-sV -sC -O -A"
    elif "тихий" in context or "stealth" in context:
        return "-sS -Pn -T2 -f"
    else:
        return "-sV --open"

def get_sqlmap_flags(context: str) -> str:
    if "быстрый" in context or "quick" in context:
        return "--batch --current-db --level=1"
    elif "полный" in context or "full" in context:
        return "--batch --dbs --tables --level=3 --risk=2"
    elif "waf" in context:
        return "--batch --dbs --level=3 --random-agent --tamper=space2comment,charencode"
    elif "тихий" in context or "stealth" in context:
        return "--batch --dbs --delay=5 --random-agent"
    else:
        return "--batch --dbs --level=1"

# ============================================================
# ЗАПУСК КОМАНД
# ============================================================

def run_command(cmd: str, timeout: int = 300) -> Dict:
    global current_process, interrupted
    
    print(f"{Colors.DIM}└─$ {cmd}{Colors.END}")
    UI.separator("─")
    
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
                print(f"\n{Colors.ICON_WARNING} Прервано{Colors.END}")
                return {"success": False, "output": "\n".join(output_lines), "interrupted": True}
            
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
        return {
            "success": current_process.returncode == 0,
            "output": "\n".join(output_lines),
            "duration": time.time() - start_time,
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
# АНАЛИЗ НАМЕРЕНИЙ
# ============================================================

class IntentAnalyzer:
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
        
        # Извлечение URL
        url_pattern = r'https?://[^\s]+|[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}(?:/\S*)?'
        urls = re.findall(url_pattern, user_input)
        
        if urls:
            result["target"] = urls[0]
            if not result["target"].startswith("http"):
                result["target"] = "http://" + result["target"]
            result["has_params"] = "?" in result["target"] and "=" in result["target"]
        
        # Если нет URL, но есть в контексте
        if not result["target"] and context_targets:
            result["target"] = context_targets[-1]
        
        # Анализ намерения
        if any(word in user_lower for word in ['sql', 'инъекц', 'sqlmap', 'проверь sql', 'найди sql']):
            result["intent"] = "sql_injection"
            result["tools"].append("sqlmap")
            result["explanation"] = "Проверка SQL-инъекций"
        
        elif any(word in user_lower for word in ['порты', 'nmap', 'скан портов']):
            result["intent"] = "port_scan"
            result["tools"].append("nmap")
            result["explanation"] = "Сканирование портов"
        
        elif any(word in user_lower for word in ['директор', 'gobuster', 'скрытые пути']):
            result["intent"] = "directory_scan"
            result["tools"].append("gobuster")
            result["explanation"] = "Поиск директорий"
        
        elif any(word in user_lower for word in ['уязвим', 'nikto', 'проверь сайт']):
            result["intent"] = "web_vulnerability"
            result["tools"].append("nikto")
            result["explanation"] = "Проверка веб-уязвимостей"
        
        elif any(word in user_lower for word in ['просканируй', 'проверь', 'протестируй']):
            result["intent"] = "general_scan"
            result["tools"].append("whatweb")
            if result["has_params"]:
                result["tools"].append("sqlmap")
            result["explanation"] = "Общее сканирование"
        
        # Если есть параметры - добавляем sqlmap
        if result["has_params"] and "sqlmap" not in result["tools"]:
            result["tools"].insert(0, "sqlmap")
        
        # Извлекаем контекстные ключевые слова для флагов
        keywords = []
        for kw in ['быстрый', 'quick', 'полный', 'full', 'агрессивный', 'aggressive', 'тихий', 'stealth', 'waf']:
            if kw in user_lower:
                keywords.append(kw)
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
        
        print(f"\n{Colors.DIM}📁 Сессия: ~/.jim/sessions/{self.id}{Colors.END}")
        UI.separator("═")

# ============================================================
# ОСНОВНОЙ АГЕНТ
# ============================================================

class JimAgent:
    def __init__(self):
        self.client = None
        self.session: Optional[Session] = None
        self.context_targets: List[str] = []
        self.paused = False
        self.auto_mode = AUTO_MODE
    
    def initialize(self):
        import openai
        self.client = openai.OpenAI(
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    def process(self, user_input: str) -> str:
        if user_input.startswith('/'):
            return self._handle_command(user_input)
        
        # Команда "sqlmap" без аргументов
        if user_input.lower().strip() == "sqlmap" and self.context_targets:
            user_input = f"проверь SQL на {self.context_targets[-1]}"
            UI.info(f"Запускаю sqlmap на {self.context_targets[-1]}")
        
        UI.thinking("Анализирую ваш запрос...", 0.3)
        
        intent = IntentAnalyzer.analyze(user_input, self.context_targets)
        
        # Сохраняем цель
        if intent["target"] and intent["target"] not in self.context_targets:
            self.context_targets.append(intent["target"])
        
        if not intent["target"]:
            return """
🔍 Не могу определить цель.

💡 Укажите:
   • URL: example.com/page?id=1
   • IP: 192.168.1.1
   • Или используйте сохранённые цели: /context

Примеры:
   • "проверь example.com/page?id=1 на SQL"
   • "найди открытые порты на 192.168.1.1"
"""
        
        if not intent["tools"]:
            return f"❓ Не понял, что делать с {intent['target']}. Уточните: проверка SQL, порты, директории?"
        
        # Создаём сессию
        self.session = Session(intent["target"])
        UI.header(intent["explanation"], Colors.ICON_ANALYSIS)
        UI.info(f"🎯 Цель: {intent['target']}")
        
        results = []
        total_tools = len(intent["tools"])
        
        for i, tool in enumerate(intent["tools"]):
            if self.paused:
                UI.warning("Сессия приостановлена. Введите /continue")
                break
            
            self.session.update_progress(i, total_tools)
            self.session.print_status()
            
            # Проверка для sqlmap
            if tool == "sqlmap" and not intent["has_params"]:
                UI.warning("В URL нет параметров! sqlmap может быть не эффективен.")
                if not self.auto_mode:
                    resp = input(f"{Colors.YELLOW}Продолжить? (y/n): {Colors.END}").strip().lower()
                    if resp != 'y':
                        continue
            
            UI.info(f"🔧 Запускаю {tool.upper()}...")
            
            if tool == "nmap":
                result = run_nmap(intent["target"], intent["context_keywords"])
                analysis = OutputAnalyzer.analyze_nmap(result["output"])
            elif tool == "sqlmap":
                result = run_sqlmap(intent["target"], intent["context_keywords"])
                analysis = OutputAnalyzer.analyze_sqlmap(result["output"])
            elif tool == "whatweb":
                result = run_whatweb(intent["target"])
                analysis = OutputAnalyzer.analyze_whatweb(result["output"])
            elif tool == "gobuster":
                result = run_gobuster(intent["target"])
                analysis = OutputAnalyzer.analyze_gobuster(result["output"])
            elif tool == "nikto":
                result = run_nikto(intent["target"])
                analysis = OutputAnalyzer.analyze_nikto(result["output"])
            else:
                continue
            
            self.session.add_result(tool, analysis, result.get("duration", 0))
            
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
            if tool == "sqlmap" and analysis.get("found"):
                UI.warning("🚨 КРИТИЧЕСКАЯ УЯЗВИМОСТЬ! Дальнейшее сканирование остановлено.")
                break
        
        self.session.update_progress(total_tools, total_tools)
        self.session.print_report()
        
        # Предложение других целей
        other_targets = [t for t in self.context_targets if t != intent["target"]]
        if other_targets:
            UI.info(f"Другие цели: {', '.join(other_targets[:2])}")
        
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
        
        elif cmd in ["context", "targets"]:
            if self.context_targets:
                result = "📋 СОХРАНЁННЫЕ ЦЕЛИ:\n"
                for i, t in enumerate(self.context_targets, 1):
                    result += f"   {i}. {t}\n"
                return result
            return "📋 Нет сохранённых целей"
        
        elif cmd in ["reset", "clear"]:
            self.context_targets = []
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
║     • /stop - остановить                                          ║
║     • /continue - продолжить                                      ║
║     • /report - итоговый отчёт                                    ║
║     • /context - показать цели                                    ║
║     • /reset - очистить память                                    ║
║     • /exit - выход                                               ║
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
    print_banner()
    
    if not check_api_key():
        sys.exit(1)
    
    agent = JimAgent()
    agent.initialize()
    
    print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}JIM ГОТОВ{Colors.END} | {Colors.ICON_SHIELD} Понимаю естественный язык")
    print(f"{Colors.ICON_INFO} Просто опишите, что нужно сделать")
    print(f"{Colors.DIM}{'='*70}{Colors.END}")
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}[{Colors.ICON_USER}]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', 'exit', 'quit']:
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
                break
            
            if not user_input:
                continue
            
            response = agent.process(user_input)
            if response:
                print(f"\n{Colors.ICON_AGENT} {response}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} {Colors.YELLOW}Прервано. /exit для выхода{Colors.END}")
            continue
        except Exception as e:
            print(f"\n{Colors.ICON_ERROR} {Colors.RED}Ошибка: {e}{Colors.END}")

if __name__ == "__main__":
    main()