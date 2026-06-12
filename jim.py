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
║                         🤖 JIM - AI PENTESTING ASSISTANT 🤖                                   ║
║                                   v2.0.0 | The Smart Agent                                   ║
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
    print(" 🔄 JIM UPDATER ".center(70, "="))
    print("="*70 + "\n")
    jim_dir = os.path.expanduser("~/.jim")
    repo_url = "https://github.com/Lolicks/hackagent.git"
    temp_dir = "/tmp/jim-update"
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print(" 📦 Cloning repository...")
        subprocess.run(["git", "clone", "--depth", "1", repo_url, temp_dir], check=True, capture_output=True)
        print(" 📄 Updating files...")
        shutil.copy2(f"{temp_dir}/jim.py", f"{jim_dir}/jim.py")
        shutil.copy2(f"{temp_dir}/system_prompt.txt", f"{jim_dir}/")
        shutil.rmtree(temp_dir)
        print("\n ✅ Update completed successfully!")
        return True
    except Exception as e:
        print(f" ❌ Update failed: {e}")
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
║                         JIM - HELP MENU                            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Usage:                                                           ║
║    jim                              → Interactive mode            ║
║    jim -a, --auto "target"          → Autonomous mode             ║
║    jim --dry-run "target"           → Preview what would happen   ║
║    jim --profile stealth|aggressive → Set default profile         ║
║    jim -h, --help                   → Show this help              ║
║    jim -v, --version                → Show version                ║
║    jim -u, --update                 → Update from GitHub          ║
║                                                                    ║
║  Interactive Commands:                                            ║
║    status, stop, skip, redo, report, save, history, undo, suggest ║
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
    """Результат сканирования одной утилитой"""
    tool: str
    status: ScanStatus
    command: str
    output: str
    analysis: Dict[str, Any]
    duration: float
    timestamp: str

@dataclass
class Session:
    """Сессия сканирования"""
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
    def status_card(session: Session):
        """Показывает текущий статус сессии"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}│ {Colors.ICON_TARGET} CURRENT SESSION{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
        print(f"{Colors.CYAN}│ Target:{Colors.END} {Colors.BOLD}{session.target}{Colors.END}")
        print(f"{Colors.CYAN}│ Phase:{Colors.END} {session.current_phase}")
        print(f"{Colors.CYAN}│ Progress:{Colors.END}")
        UI.progress_bar(int(session.progress))
        print(f"{Colors.CYAN}│ Findings:{Colors.END} {len(session.found_vulnerabilities)} vulnerabilities found")
        print(f"{Colors.CYAN}│ Tools run:{Colors.END} {len(session.scan_history)}")
        print(f"{Colors.CYAN}│ Duration:{Colors.END} {session.start_time}")
        print(f"{Colors.BOLD}{Colors.CYAN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
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
    """Создаёт необходимые директории"""
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
    """Возвращает флаги и пояснение"""
    flags = "-sV --open"
    explanation = "Standard port scan with service version detection"
    
    if "все порты" in context.lower() or "full" in context.lower():
        flags = "-sV -p- --open --min-rate=1000"
        explanation = "Full port scan (1-65535) with rate limiting"
    elif "быстрый" in context.lower() or "quick" in context.lower():
        flags = "-F --open"
        explanation = "Quick scan (top 100 ports only)"
    elif "агрессивный" in context.lower() or "aggressive" in context.lower():
        flags = "-sV -sC -O --open --version-intensity=9"
        explanation = "Aggressive scan: versions, scripts, OS detection"
    elif "udp" in context.lower():
        flags = "-sU --open"
        explanation = "UDP port scan"
    elif profile == "stealth":
        flags = "-sS -Pn -T2 -f --data-length=200 --randomize-hosts --spoof-mac 0"
        explanation = "Stealth mode: SYN scan, no ping, slow timing, fragmentation"
    elif profile == "aggressive":
        flags = "-sV -sC -O -A -T4 -p-"
        explanation = "Aggressive profile: all ports, OS, versions, traceroute"
    
    return flags, explanation

def get_sqlmap_flags(url: str, context: str = "", profile: str = "normal") -> Tuple[str, str]:
    flags = "--batch --dbs --level=1"
    explanation = "Standard SQL injection scan, database enumeration"
    
    if "полный" in context.lower() or "full" in context.lower():
        flags = "--batch --dbs --tables --level=3 --risk=2"
        explanation = "Full enumeration: databases, tables, columns"
    elif "быстрый" in context.lower() or "quick" in context.lower():
        flags = "--batch --current-db --level=1"
        explanation = "Quick scan: current database only"
    elif "os-shell" in context.lower():
        flags = "--batch --os-shell"
        explanation = "DANGEROUS: Attempt OS shell access"
    elif "waf" in context.lower():
        flags = "--batch --dbs --level=3 --risk=2 --random-agent --tamper=space2comment,charencode"
        explanation = "WAF bypass mode with tamper scripts"
    elif profile == "stealth":
        flags = "--batch --dbs --level=1 --delay=5 --random-agent --tor --check-tor"
        explanation = "Stealth mode: delays, Tor, random User-Agent"
    elif profile == "aggressive":
        flags = "--batch --dbs --tables --level=5 --risk=3 --threads=10"
        explanation = "Aggressive mode: high level/risk, multi-threaded"
    
    return flags, explanation

def get_gobuster_flags(url: str, context: str = "", profile: str = "normal") -> Tuple[str, str]:
    wordlist = "/usr/share/wordlists/dirb/common.txt"
    flags = f"dir -u {url} -w {wordlist}"
    explanation = "Directory brute-force with common wordlist"
    
    if "большой" in context.lower() or "big" in context.lower():
        wordlist = "/usr/share/wordlists/dirb/big.txt"
        flags = f"dir -u {url} -w {wordlist}"
        explanation = "Large wordlist mode (big.txt)"
    elif "расширение" in context.lower() or "extension" in context.lower():
        flags = f"dir -u {url} -w {wordlist} -x php,txt,html,asp,aspx,js,css,json,xml,bak,old,sql"
        explanation = "Extension search mode"
    elif profile == "stealth":
        flags = f"dir -u {url} -w {wordlist} -t 10 --delay 2"
        explanation = "Stealth mode: slow requests, low threads"
    elif profile == "aggressive":
        flags = f"dir -u {url} -w {wordlist} -t 50"
        explanation = "Aggressive mode: high thread count"
    
    return flags, explanation

def get_nikto_flags(target: str, context: str = "", profile: str = "normal") -> Tuple[str, str]:
    flags = f"-h {target}"
    explanation = "Standard web vulnerability scan"
    
    if "ssl" in context.lower() or "https" in context.lower():
        flags = f"-h {target} -ssl"
        explanation = "SSL/HTTPS mode"
    elif "агрессивный" in context.lower() or "aggressive" in context.lower():
        flags = f"-h {target} -maxtime=600 -Tuning=4"
        explanation = "Aggressive scan: longer timeout, specific tuning"
    elif profile == "stealth":
        flags = f"-h {target} -delay 5 -nossl"
        explanation = "Stealth mode: request delays"
    
    return flags, explanation

def get_whatweb_flags(target: str, context: str = "", profile: str = "normal") -> Tuple[str, str]:
    flags = target
    explanation = "Basic technology detection"
    
    if "подробный" in context.lower() or "verbose" in context.lower():
        flags = f"-v {target}"
        explanation = "Verbose output mode"
    elif "агрессивный" in context.lower() or "aggressive" in context.lower():
        flags = f"-a 3 {target}"
        explanation = "Aggressive plugin mode (more plugins)"
    elif profile == "stealth":
        flags = f"-a 1 {target}"
        explanation = "Stealth mode: light plugin set"
    
    return flags, explanation

# ============================================================
# АНАЛИЗ ЦЕЛИ
# ============================================================

class TargetAnalyzer:
    """Анализирует цель и определяет стратегию"""
    
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
        
        # Извлечение IP
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ip_matches = re.findall(ip_pattern, user_input)
        if ip_matches:
            result["target_type"] = "ip"
            result["target"] = ip_matches[0]
            result["explanation"] = f"IP address detected: {ip_matches[0]}"
            result["suggested_tools"] = ["nmap"]
        
        # Извлечение URL
        url_pattern = r'https?://[^\s]+|[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}[^\s]*'
        url_matches = re.findall(url_pattern, user_input)
        if url_matches:
            url = url_matches[0]
            if not url.startswith("http"):
                url = "http://" + url
            result["target_type"] = "url"
            result["target"] = url
            result["has_parameters"] = "?" in url and "=" in url
            result["explanation"] = f"URL detected: {url}"
            result["suggested_tools"] = ["whatweb"]
            if result["has_parameters"]:
                result["suggested_tools"].insert(0, "sqlmap")
                result["explanation"] += " | Parameters found → SQL injection test priority"
        
        # Извлечение ключевых слов
        keywords = ["sql", "инъекц", "injection", "директори", "directory", 
                    "порт", "port", "уязвим", "vulnerab", "скан", "scan"]
        for kw in keywords:
            if kw in user_input.lower():
                result["keywords"].append(kw)
        
        # Корректировка на основе ключевых слов
        if "sql" in result["keywords"] or "инъекц" in result["keywords"]:
            if "sqlmap" not in result["suggested_tools"]:
                result["suggested_tools"].insert(0, "sqlmap")
        
        return result

# ============================================================
# АНАЛИЗ ВЫВОДА
# ============================================================

class OutputAnalyzer:
    """Анализирует вывод утилит и извлекает смысл"""
    
    @staticmethod
    def analyze_nmap(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        open_ports = re.findall(r'(\d+)/tcp\s+open\s+(\w+)', output)
        if open_ports:
            analysis["found"] = True
            analysis["summary"] = f"🔓 {len(open_ports)} open ports discovered"
            
            web_ports = []
            db_ports = []
            other_ports = []
            
            for port, service in open_ports:
                analysis["details"].append(f"Port {port}: {service}")
                if port in ["80", "443", "8080", "8443"]:
                    web_ports.append(port)
                    analysis["insights"].append(f"🌐 Web server detected on port {port}")
                elif service in ["mysql", "postgresql", "mongodb", "redis"]:
                    db_ports.append(port)
                    analysis["insights"].append(f"🗄️ Database ({service}) on port {port}")
                else:
                    other_ports.append(port)
            
            if not analysis["insights"]:
                analysis["insights"].append("ℹ️ No web or database services detected")
        else:
            analysis["summary"] = "🔒 No open ports found"
            analysis["insights"].append("⚠️ Target may be down or firewall blocking")
        
        return analysis
    
    @staticmethod
    def analyze_sqlmap(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        if "vulnerable" in output.lower() or "injectable" in output.lower():
            analysis["found"] = True
            analysis["summary"] = "🐛 SQL Injection VULNERABLE!"
            
            if "boolean" in output.lower():
                analysis["details"].append("Type: Boolean-based Blind SQLi")
                analysis["insights"].append("🎯 Boolean-based: Can extract data bit by bit")
            if "union" in output.lower():
                analysis["details"].append("Type: Union-based SQLi")
                analysis["insights"].append("🎯 Union-based: Fast data extraction")
            if "time" in output.lower():
                analysis["details"].append("Type: Time-based Blind SQLi")
                analysis["insights"].append("🎯 Time-based: Works even with no visible output")
            
            # Поиск баз данных
            dbs = re.findall(r'\[\*\*\]\s+(\w+)', output)
            if dbs:
                analysis["details"].append(f"Databases found: {', '.join(dbs[:5])}")
                analysis["insights"].append(f"📊 Database enumeration successful: {len(dbs)} databases")
        else:
            analysis["summary"] = "🛡️ SQL Injection NOT vulnerable"
            if "waf" in output.lower():
                analysis["insights"].append("🛡️ WAF detected - target may be protected")
        
        return analysis
    
    @staticmethod
    def analyze_gobuster(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        dirs = re.findall(r'/(\S+)\s+\(Status:\s+(\d+)\)', output)
        interesting = [d for d in dirs if d[1] in ["200", "301", "302", "401", "403"]]
        
        if interesting:
            analysis["found"] = True
            analysis["summary"] = f"📁 {len(interesting)} interesting directories found"
            
            for path, status in interesting[:15]:
                analysis["details"].append(f"/{path} (HTTP {status})")
                if status == "200":
                    analysis["insights"].append(f"📄 Accessible: /{path}")
                elif status == "401":
                    analysis["insights"].append(f"🔒 Authentication required: /{path}")
                elif status == "403":
                    analysis["insights"].append(f"🚫 Forbidden but exists: /{path}")
        else:
            analysis["summary"] = "📭 No interesting directories found"
        
        return analysis
    
    @staticmethod
    def analyze_nikto(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        # Ищем уязвимости
        vuln_pattern = r'\+ (.*?):'
        all_vulns = re.findall(vuln_pattern, output)
        
        critical_keywords = ['cve', 'vulnerable', 'rce', 'remote', 'execution', 'injection', 'sql', 'xss']
        critical = [v for v in all_vulns if any(k in v.lower() for k in critical_keywords)]
        
        if critical:
            analysis["found"] = True
            analysis["summary"] = f"⚠️ {len(critical)} potential vulnerabilities found"
            for v in critical[:10]:
                analysis["details"].append(v[:80])
                if 'cve' in v.lower():
                    analysis["insights"].append(f"🔴 Known CVE detected: {v[:50]}")
        
        # Ищем информацию о сервере
        server_match = re.search(r'\+ Server:\s*(.+?)(?:\n|$)', output, re.IGNORECASE)
        if server_match:
            analysis["insights"].append(f"🖥️ Server: {server_match.group(1).strip()}")
        
        if not analysis["found"]:
            analysis["summary"] = "🛡️ No obvious vulnerabilities detected"
        
        return analysis
    
    @staticmethod
    def analyze_whatweb(output: str) -> Dict[str, Any]:
        analysis = {"found": False, "summary": "", "details": [], "insights": []}
        
        techs = re.findall(r'\[(.*?)\]', output)
        clean_techs = []
        
        for t in techs:
            if 'http' not in t.lower() and len(t) < 50 and t not in clean_techs:
                clean_techs.append(t)
        
        if clean_techs:
            analysis["found"] = True
            analysis["summary"] = f"🔧 {len(clean_techs)} technologies detected"
            for t in clean_techs[:15]:
                analysis["details"].append(t)
            
            # Инсайты на основе технологий
            cms_list = ['WordPress', 'Joomla', 'Drupal', 'Magento']
            for tech in clean_techs:
                if tech in cms_list:
                    analysis["insights"].append(f"📰 CMS detected: {tech} - consider CMS-specific tools")
                elif 'nginx' in tech.lower():
                    analysis["insights"].append("⚡ Nginx detected - check misconfigurations")
                elif 'apache' in tech.lower():
                    analysis["insights"].append("🔄 Apache detected - consider version-specific CVEs")
                elif 'php' in tech.lower():
                    analysis["insights"].append("🐘 PHP detected - check for file inclusion, RCE")
        else:
            analysis["summary"] = "❓ Technologies not clearly detected"
        
        return analysis

# ============================================================
# ЗАПУСК УТИЛИТ
# ============================================================

def run_command(cmd: str, timeout: int = 300, show_output: bool = True) -> Dict:
    """Запускает команду с возможностью прерывания"""
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
                print(f"\n{Colors.ICON_WARNING} {Colors.YELLOW}Interrupted by user{Colors.END}")
                return {"success": False, "output": "\n".join(output_lines), "interrupted": True}
            
            if line:
                output_lines.append(line.rstrip())
                if show_output:
                    # Премиум подсветка
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
        UI.info(f"Strategy: {explanation}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} NMAP SCAN{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.CYAN}│ Target:{Colors.END} {Colors.BOLD}{target}{Colors.END}")
    print(f"{Colors.CYAN}│ Flags:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    cmd = f"nmap {flags} {target}"
    return run_command(cmd, timeout=600)

def run_sqlmap(url: str, flags: str = None, context: str = "", profile: str = "normal") -> Dict:
    if flags is None:
        flags, explanation = get_sqlmap_flags(url, context, profile)
        UI.info(f"Strategy: {explanation}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} SQLMAP SCAN{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.CYAN}│ Target:{Colors.END} {Colors.BOLD}{url}{Colors.END}")
    print(f"{Colors.CYAN}│ Flags:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    cmd = f"sqlmap -u '{url}' {flags}"
    return run_command(cmd, timeout=1200)

def run_gobuster(url: str, flags: str = None, context: str = "", profile: str = "normal") -> Dict:
    if flags is None:
        flags, explanation = get_gobuster_flags(url, context, profile)
        UI.info(f"Strategy: {explanation}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} GOBUSTER SCAN{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.CYAN}│ Target:{Colors.END} {Colors.BOLD}{url}{Colors.END}")
    print(f"{Colors.CYAN}│ Flags:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    cmd = f"gobuster {flags}"
    return run_command(cmd, timeout=600)

def run_nikto(target: str, flags: str = None, context: str = "", profile: str = "normal") -> Dict:
    if flags is None:
        flags, explanation = get_nikto_flags(target, context, profile)
        UI.info(f"Strategy: {explanation}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} NIKTO SCAN{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.CYAN}│ Target:{Colors.END} {Colors.BOLD}{target}{Colors.END}")
    print(f"{Colors.CYAN}│ Flags:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    cmd = f"nikto {flags}"
    return run_command(cmd, timeout=900)

def run_whatweb(target: str, flags: str = None, context: str = "", profile: str = "normal") -> Dict:
    if flags is None:
        flags, explanation = get_whatweb_flags(target, context, profile)
        UI.info(f"Strategy: {explanation}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} WHATWEB SCAN{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.CYAN}│ Target:{Colors.END} {Colors.BOLD}{target}{Colors.END}")
    print(f"{Colors.CYAN}│ Flags:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
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
        self.current_phase = "Initializing"
        self.progress = 0
        self.context = {}
        self.paused = False
        self.current_process = None
        
        # Пути для сохранения
        self.session_dir = os.path.expanduser(f"~/.jim/sessions/{self.session_id}")
        os.makedirs(self.session_dir, exist_ok=True)
    
    def add_result(self, result: ScanResult):
        self.scan_history.append(result)
        self._extract_findings(result)
        self._update_progress()
        self._save_session()
    
    def _extract_findings(self, result: ScanResult):
        """Извлекает находки из результата"""
        if result.tool == "nmap":
            # Извлечение открытых портов
            ports = re.findall(r'(\d+)/tcp\s+open', result.output)
            self.discovered_ports = list(set(self.discovered_ports + [int(p) for p in ports]))
            
            # Проверка на интересные сервисы
            if any(p in self.discovered_ports for p in [80, 443, 8080]):
                self.found_vulnerabilities.append({
                    "severity": "info",
                    "type": "web_service",
                    "description": "Web service detected",
                    "timestamp": result.timestamp
                })
        
        elif result.tool == "sqlmap" and result.analysis.get("found"):
            self.found_vulnerabilities.append({
                "severity": "critical",
                "type": "sql_injection",
                "description": result.analysis.get("summary", "SQL Injection found"),
                "details": result.analysis.get("details", []),
                "timestamp": result.timestamp
            })
        
        elif result.tool == "whatweb" and result.analysis.get("found"):
            # Извлечение технологий
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
        """Обновляет прогресс на основе количества выполненных сканов"""
        # Простая эвристика: каждый завершённый инструмент даёт 10-15% прогресса
        self.progress = min(100, len(self.scan_history) * 12)
    
    def _save_session(self):
        """Сохраняет сессию в JSON"""
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
        """Показывает текущий статус сессии"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}│ {Colors.ICON_TARGET} SESSION STATUS{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
        print(f"{Colors.CYAN}│ Session:{Colors.END} {self.session_id}")
        print(f"{Colors.CYAN}│ Target:{Colors.END} {Colors.BOLD}{self.target}{Colors.END}")
        print(f"{Colors.CYAN}│ Phase:{Colors.END} {self.current_phase}")
        print(f"{Colors.CYAN}│ Progress:{Colors.END}")
        UI.progress_bar(int(self.progress))
        print(f"{Colors.CYAN}│ Tools run:{Colors.END} {len(self.scan_history)}")
        print(f"{Colors.CYAN}│ Vulnerabilities:{Colors.END} {len(self.found_vulnerabilities)}")
        print(f"{Colors.CYAN}│ Duration:{Colors.END} {str(datetime.now() - self.start_time).split('.')[0]}")
        
        if self.found_vulnerabilities:
            print(f"{Colors.CYAN}│ Findings:{Colors.END}")
            for vuln in self.found_vulnerabilities[:3]:
                severity_color = Colors.RED if vuln["severity"] == "critical" else Colors.YELLOW
                print(f"{Colors.DIM}│   {severity_color}▪ {vuln['description'][:50]}{Colors.END}")
        
        print(f"{Colors.BOLD}{Colors.CYAN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    def print_final_report(self):
        """Печатает итоговый отчёт"""
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{Colors.ICON_REPORT} FINAL ASSESSMENT REPORT{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")
        
        print(f"\n{Colors.CYAN}🎯 Target:{Colors.END} {Colors.BOLD}{self.target}{Colors.END}")
        print(f"{Colors.CYAN}⏱️ Duration:{Colors.END} {str(duration).split('.')[0]}")
        print(f"{Colors.CYAN}🛠️ Tools used:{Colors.END} {len(self.scan_history)}")
        
        # Сортировка уязвимостей по критичности
        critical = [v for v in self.found_vulnerabilities if v["severity"] == "critical"]
        high = [v for v in self.found_vulnerabilities if v["severity"] == "high"]
        medium = [v for v in self.found_vulnerabilities if v["severity"] == "medium"]
        
        if critical:
            print(f"\n{Colors.BG_RED}{Colors.BOLD}{Colors.WHITE}🔴 CRITICAL VULNERABILITIES{Colors.END}")
            for v in critical:
                print(f"   • {v['description']}")
        
        if high:
            print(f"\n{Colors.RED}{Colors.BOLD}🟠 HIGH RISK{Colors.END}")
            for v in high:
                print(f"   • {v['description']}")
        
        if medium:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}🟡 MEDIUM RISK{Colors.END}")
            for v in medium:
                print(f"   • {v['description']}")
        
        if self.technologies:
            print(f"\n{Colors.CYAN}{Colors.BOLD}🔧 TECHNOLOGIES DETECTED{Colors.END}")
            for tech in self.technologies[:10]:
                print(f"   • {tech}")
        
        if self.discovered_ports:
            print(f"\n{Colors.CYAN}{Colors.BOLD}🔌 OPEN PORTS{Colors.END}")
            print(f"   {', '.join(map(str, self.discovered_ports[:15]))}")
        
        # Рекомендации
        print(f"\n{Colors.GREEN}{Colors.BOLD}💡 RECOMMENDATIONS{Colors.END}")
        if critical:
            print(f"   • Patch critical vulnerabilities immediately")
        if any('sql' in str(v).lower() for v in critical):
            print(f"   • Use parameterized queries to prevent SQL injection")
        if 'WordPress' in self.technologies:
            print(f"   • Run wpscan for WordPress-specific vulnerabilities")
        if not self.found_vulnerabilities:
            print(f"   • No obvious vulnerabilities found. Consider manual testing.")
        
        print(f"\n{Colors.DIM}📁 Session saved to: ~/.jim/sessions/{self.session_id}/{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'═' * 70}{Colors.END}")

# ============================================================
# ОСНОВНОЙ АГЕНТ
# ============================================================

class JimAgent:
    def __init__(self):
        if not API_KEY:
            UI.error("API key not found!")
            UI.info("Run ./install.sh to configure")
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
        # Обработка команд
        if user_input.startswith('/'):
            return self._handle_command(user_input)
        
        # Анализ цели
        UI.loading_animation("Analyzing target...", 0.3)
        analysis = TargetAnalyzer.analyze(user_input)
        
        if not analysis["target"]:
            return "❌ Could not identify target. Please provide an IP address or URL."
        
        # Создаём сессию
        self.session = JimSession(analysis["target"])
        self.session.current_phase = "Analyzing target"
        self.session.print_status()
        
        # Планирование и выполнение
        return self._execute_plan(analysis)
    
    def _execute_plan(self, analysis: Dict) -> str:
        """Выполняет план сканирования"""
        target = analysis["target"]
        suggested_tools = analysis["suggested_tools"]
        
        if self.dry_run:
            return self._dry_run_report(analysis)
        
        results = []
        
        for tool in suggested_tools:
            if self.session.paused:
                UI.warning("Session paused. Type 'continue' to resume")
                break
            
            self.session.current_phase = f"Running {tool}"
            self.session.print_status()
            
            if not self.auto_mode:
                print(f"\n{Colors.YELLOW}📋 Next: {tool.upper()} on {target}{Colors.END}")
                response = input(f"{Colors.CYAN}Run this tool? (y/n/skip/auto): {Colors.END}").strip().lower()
                if response == 'n':
                    UI.info("Skipping...")
                    continue
                elif response == 'auto':
                    self.auto_mode = True
                elif response == 'skip':
                    UI.info("Skipping...")
                    continue
            
            # Запуск инструмента
            result = self._run_tool(tool, target, analysis.get("keywords", []))
            
            if result and result.get("interrupted"):
                UI.warning("Scan interrupted by user")
                break
            
            if result:
                # Анализ результата
                analysis_result = self._analyze_tool_output(tool, result.get("output", ""))
                
                # Сохраняем результат
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
                
                # Показываем анализ
                self._print_analysis(tool, analysis_result)
                
                # Проверка на критическую находку
                if analysis_result.get("found") and tool == "sqlmap":
                    UI.warning("CRITICAL: SQL Injection found! Stopping further scans.")
                    break
        
        # Итоговый отчёт
        self.session.print_final_report()
        
        return "✅ Assessment completed"
    
    def _run_tool(self, tool: str, target: str, keywords: List[str]) -> Dict:
        """Запускает указанный инструмент"""
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
        else:
            return {"success": False, "error": f"Unknown tool: {tool}"}
    
    def _analyze_tool_output(self, tool: str, output: str) -> Dict:
        """Анализирует вывод инструмента"""
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
        return {"found": False, "summary": "Unknown tool", "details": [], "insights": []}
    
    def _print_analysis(self, tool: str, analysis: Dict):
        """Печатает анализ результатов"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}│ {Colors.ICON_ANALYSIS} ANALYSIS - {tool.upper()}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
        
        if analysis.get("found"):
            print(f"{Colors.DIM}│{Colors.END} {Colors.GREEN}{analysis.get('summary', 'Findings detected')}{Colors.END}")
        else:
            print(f"{Colors.DIM}│{Colors.END} {Colors.YELLOW}{analysis.get('summary', 'No findings')}{Colors.END}")
        
        for insight in analysis.get("insights", [])[:5]:
            print(f"{Colors.DIM}│{Colors.END}   {insight}")
        
        for detail in analysis.get("details", [])[:5]:
            print(f"{Colors.DIM}│{Colors.END}   • {detail}")
        
        print(f"{Colors.BOLD}{Colors.CYAN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    def _dry_run_report(self, analysis: Dict) -> str:
        """Создаёт отчёт для dry-run режима"""
        target = analysis["target"]
        suggested_tools = analysis["suggested_tools"]
        
        report = f"""
{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}
{Colors.BOLD}{Colors.CYAN}{Colors.ICON_SPARKLES} DRY RUN MODE - What would happen{Colors.END}
{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}

🎯 Target: {target}
📋 Detected type: {analysis['target_type']}
🔍 Keywords: {', '.join(analysis['keywords']) if analysis['keywords'] else 'none'}

📊 Proposed scan plan:
"""
        for i, tool in enumerate(suggested_tools, 1):
            flags, explanation = self._get_default_flags(tool, target)
            report += f"""
{i}. {tool.upper()}
   → Flags: {flags}
   → Why: {explanation}
"""
        
        report += f"""
{Colors.YELLOW}ℹ️ No actual scans were performed. Run without --dry-run to execute.{Colors.END}
{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.END}
"""
        return report
    
    def _get_default_flags(self, tool: str, target: str) -> Tuple[str, str]:
        """Возвращает флаги по умолчанию для dry-run"""
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
        """Обрабатывает интерактивные команды"""
        cmd = command.lower().strip('/')
        
        if cmd in ["status", "stats"]:
            if self.session:
                self.session.print_status()
                return ""
            return "No active session"
        
        elif cmd in ["stop", "pause"]:
            if self.session:
                self.session.paused = True
                return "⏸️ Session paused. Type 'continue' to resume"
            return "No active session"
        
        elif cmd in ["continue", "resume"]:
            if self.session:
                self.session.paused = False
                return "▶️ Session resumed"
            return "No active session"
        
        elif cmd in ["report", "summary"]:
            if self.session:
                self.session.print_final_report()
                return ""
            return "No active session"
        
        elif cmd in ["save", "export"]:
            if self.session:
                self.session._save_session()
                return f"💾 Session saved to ~/.jim/sessions/{self.session.session_id}/"
            return "No active session"
        
        elif cmd in ["history", "log"]:
            if self.session:
                print(f"\n{Colors.BOLD}📋 Scan History:{Colors.END}")
                for i, scan in enumerate(self.session.scan_history, 1):
                    status_icon = Colors.ICON_SUCCESS if scan.status == ScanStatus.COMPLETED else Colors.ICON_ERROR
                    print(f"  {i}. {status_icon} {scan.tool} - {scan.duration:.1f}s")
                return ""
            return "No active session"
        
        elif cmd in ["help", "?"]:
            return """
╔════════════════════════════════════════════════════════════════════╗
║                      INTERACTIVE COMMANDS                          ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  /status, /stats   - Show current session status                  ║
║  /stop, /pause     - Pause current scan                           ║
║  /continue, /resume- Resume paused scan                           ║
║  /report, /summary - Show final report                            ║
║  /save, /export    - Save current session                         ║
║  /history, /log    - Show scan history                            ║
║  /help, /?         - Show this help                               ║
║  /exit, /quit      - Exit Jim                                     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
"""
        
        return f"Unknown command: {command}. Type /help for available commands"

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
║                         🤖 JIM - AI PENTESTING ASSISTANT 🤖                                   ║
║                                   v2.0.0 | The Smart Agent                                   ║
║                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
"""
    print(f"{Colors.CYAN}{banner}{Colors.END}")
    print(f"{Colors.DIM}{'='*70}{Colors.END}")
    print(f"{Colors.ICON_ROCKET} {Colors.GREEN}Jim initialized{Colors.END} | {Colors.ICON_SHIELD} Ready for action")
    print(f"{Colors.ICON_INFO} Commands: {Colors.YELLOW}/help{Colors.END} | /status{Colors.END} | /stop{Colors.END} | /report{Colors.END}")
    print(f"{Colors.ICON_FLAG} Profile: {Colors.BOLD}{PROFILE}{Colors.END} | Mode: {Colors.BOLD}{'Auto' if AUTO_MODE else 'Interactive'}{Colors.END}")
    print(f"{Colors.DIM}{'='*70}{Colors.END}")

def main():
    print_banner()
    agent = JimAgent()
    
    # Автономный режим
    if AUTO_MODE and len(sys.argv) > 2:
        target = ' '.join(sys.argv[2:])
        print(f"\n{Colors.ICON_AGENT} {Colors.BLUE}Autonomous mode: Scanning {target}{Colors.END}")
        response = agent.process(target)
        print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}Done!{Colors.END}")
        return
    
    # Интерактивный режим
    print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}Interactive mode. Type your target or /help{Colors.END}")
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}[{Colors.ICON_USER} jim]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}See you next time!{Colors.END}\n")
                break
            
            if not user_input:
                continue
            
            response = agent.process(user_input)
            if response:
                print(f"\n{Colors.ICON_AGENT} {response}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} {Colors.YELLOW}Interrupted. Type /exit to quit{Colors.END}")
            continue
        except EOFError:
            print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}Goodbye!{Colors.END}\n")
            break

if __name__ == "__main__":
    main()