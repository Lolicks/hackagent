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
from datetime import datetime
from typing import Dict, Any, List, Optional

# ============================================================
# ОБРАБОТКА АРГУМЕНТОВ
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

if len(sys.argv) > 1:
    if sys.argv[1] in ["-v", "--version"]:
        print(f"JIM AI Agent v{VERSION}")
        sys.exit(0)
    elif sys.argv[1] in ["-h", "--help"]:
        print("""
╔════════════════════════════════════════════════════════════════════╗
║                         JIM - HELP MENU                            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Usage:                                                           ║
║    jim                    → Launch interactive mode               ║
║    jim -h, --help         → Show this help                        ║
║    jim -v, --version      → Show version                          ║
║    jim -u, --update       → Update from GitHub                    ║
║                                                                    ║
║  Interactive Commands:                                            ║
║    /help, /?              → Show help                             ║
║    /clear, /cls           → Clear screen                          ║
║    /exit, /quit           → Exit Jim                              ║
║                                                                    ║
║  Examples:                                                        ║
║    > Test website example.com for vulnerabilities                 ║
║    > Scan SQL injection on testphp.vulnweb.com/artists.php?id=1  ║
║    > Aggressive nmap scan on 192.168.1.1                         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")
        sys.exit(0)
    elif sys.argv[1] in ["-u", "--update"]:
        sys.exit(0 if update_jim() else 1)

# ============================================================
# ПРЕМИУМ ЦВЕТОВАЯ СХЕМА
# ============================================================

class Colors:
    # Основные цвета
    BLACK = '\033[30m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Стили
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    END = '\033[0m'
    
    # Фоновые цвета
    BG_BLACK = '\033[40m'
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    BG_PURPLE = '\033[105m'
    BG_CYAN = '\033[106m'
    BG_WHITE = '\033[107m'
    
    # Иконки (Unicode)
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

# ============================================================
# ПРЕМИУМ UI КОМПОНЕНТЫ
# ============================================================

class UI:
    """Премиум UI компоненты"""
    
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
    def tool_start(tool: str, flags: str, target: str):
        print(f"\n{Colors.BOLD}{Colors.PURPLE}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}│ {Colors.ICON_TOOL} {tool.upper()}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
        print(f"{Colors.CYAN}│ Target:{Colors.END} {Colors.BOLD}{target}{Colors.END}")
        print(f"{Colors.CYAN}│ Flags:{Colors.END}  {Colors.YELLOW}{flags}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
    
    @staticmethod
    def analysis_result(found: bool, summary: str, details: list):
        status_icon = Colors.ICON_SUCCESS if found else Colors.ICON_WARNING
        status_color = Colors.GREEN if found else Colors.YELLOW
        print(f"\n{status_color}{status_icon} {summary}{Colors.END}")
        for detail in details[:5]:
            print(f"   {Colors.DIM}•{Colors.END} {detail}")
    
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
    
    @staticmethod
    def print_box(content: str, title: str = "", color: str = Colors.CYAN):
        lines = content.split('\n')
        width = max(len(line) for line in lines) + 4
        width = min(width, 80)
        
        if title:
            print(f"{color}┌{'─' * (width - 2)}┐{Colors.END}")
            print(f"{color}│ {Colors.BOLD}{title}{Colors.END}{' ' * (width - len(title) - 3)}{color}│{Colors.END}")
            print(f"{color}├{'─' * (width - 2)}┤{Colors.END}")
        else:
            print(f"{color}┌{'─' * (width - 2)}┐{Colors.END}")
        
        for line in lines:
            padding = width - len(line) - 2
            print(f"{color}│ {line}{' ' * padding}{color}│{Colors.END}")
        
        print(f"{color}└{'─' * (width - 2)}┘{Colors.END}")

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

API_KEY = load_api_key()
SYSTEM_PROMPT = load_system_prompt()

# ============================================================
# УМНЫЙ ВЫБОР ФЛАГОВ
# ============================================================

def get_nmap_flags(target: str, context: str = "") -> str:
    flags = "-sV --open"
    if "все порты" in context.lower() or "full" in context.lower():
        flags = "-sV -p- --open"
        UI.info("Full port scan mode active")
    elif "быстрый" in context.lower() or "quick" in context.lower():
        flags = "-F --open"
        UI.info("Quick scan mode active")
    elif "агрессивный" in context.lower() or "aggressive" in context.lower():
        flags = "-sV -sC -O --open"
        UI.info("Aggressive scan mode active")
    elif "udp" in context.lower():
        flags = "-sU --open"
        UI.info("UDP scan mode active")
    return flags

def get_sqlmap_flags(url: str, context: str = "") -> str:
    flags = "--batch --dbs --level=1"
    if "полный" in context.lower() or "full" in context.lower():
        flags = "--batch --dbs --tables --level=3 --risk=2"
        UI.info("Full database enumeration mode")
    elif "быстрый" in context.lower() or "quick" in context.lower():
        flags = "--batch --current-db --level=1"
        UI.info("Quick scan mode")
    elif "os-shell" in context.lower():
        flags = "--batch --os-shell"
        UI.warning("OS shell attempt mode - DANGEROUS")
    elif "waf" in context.lower():
        flags = "--batch --dbs --level=3 --risk=2 --random-agent --tamper=space2comment"
        UI.info("WAF bypass mode active")
    return flags

def get_gobuster_flags(url: str, context: str = "") -> str:
    wordlist = "/usr/share/wordlists/dirb/common.txt"
    flags = f"dir -u {url} -w {wordlist}"
    if "большой" in context.lower() or "big" in context.lower():
        wordlist = "/usr/share/wordlists/dirb/big.txt"
        flags = f"dir -u {url} -w {wordlist}"
        UI.info("Big wordlist mode")
    elif "расширение" in context.lower() or "extension" in context.lower():
        flags = f"dir -u {url} -w {wordlist} -x php,txt,html,asp,aspx,js,css,json,xml"
        UI.info("Extension search mode")
    return flags

def get_nikto_flags(target: str, context: str = "") -> str:
    flags = f"-h {target}"
    if "ssl" in context.lower() or "https" in context.lower():
        flags = f"-h {target} -ssl"
        UI.info("SSL/HTTPS mode")
    elif "агрессивный" in context.lower() or "aggressive" in context.lower():
        flags = f"-h {target} -maxtime=600 -Tuning=4"
        UI.info("Aggressive scan mode")
    return flags

def get_whatweb_flags(target: str, context: str = "") -> str:
    flags = target
    if "подробный" in context.lower() or "verbose" in context.lower():
        flags = f"-v {target}"
        UI.info("Verbose output mode")
    elif "агрессивный" in context.lower() or "aggressive" in context.lower():
        flags = f"-a 3 {target}"
        UI.info("Aggressive plugin mode")
    return flags

# ============================================================
# ЗАПУСК УТИЛИТ
# ============================================================

def run_command(cmd: str, timeout: int = 300, show_flags: bool = True):
    if show_flags:
        print(f"{Colors.DIM}└─$ {cmd}{Colors.END}")
    UI.separator("─", 70, Colors.DIM)
    
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        output_lines = []
        for line in iter(process.stdout.readline, ''):
            if line:
                output_lines.append(line.rstrip())
                # Премиум подсветка
                if 'vulnerable' in line.lower() or 'injectable' in line.lower():
                    print(f"{Colors.BG_RED}{Colors.BOLD}{Colors.WHITE}{line.rstrip()}{Colors.END}")
                elif 'open' in line.lower() and 'tcp' in line.lower():
                    print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                elif 'error' in line.lower():
                    print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                elif 'database' in line.lower():
                    print(f"{Colors.CYAN}{line.rstrip()}{Colors.END}")
                elif 'table' in line.lower():
                    print(f"{Colors.PURPLE}{line.rstrip()}{Colors.END}")
                elif 'found' in line.lower() or 'discovered' in line.lower():
                    print(f"{Colors.YELLOW}{line.rstrip()}{Colors.END}")
                else:
                    print(f"{Colors.DIM}{line.rstrip()}{Colors.END}")
        
        process.wait(timeout=timeout)
        return {"success": process.returncode == 0, "output": "\n".join(output_lines)}
    except subprocess.TimeoutExpired:
        process.terminate()
        UI.error(f"Command timeout after {timeout}s")
        return {"success": False, "output": "", "error": "Timeout"}
    except Exception as e:
        UI.error(str(e))
        return {"success": False, "output": "", "error": str(e)}

def run_nmap(target: str, flags: str = None, context: str = ""):
    if flags is None:
        flags = get_nmap_flags(target, context)
    UI.tool_start("NMAP", flags, target)
    cmd = f"nmap {flags} {target}"
    return run_command(cmd, timeout=300)

def run_sqlmap(url: str, flags: str = None, context: str = ""):
    if flags is None:
        flags = get_sqlmap_flags(url, context)
    UI.tool_start("SQLMAP", flags, url)
    cmd = f"sqlmap -u '{url}' {flags}"
    return run_command(cmd, timeout=600)

def run_gobuster(url: str, flags: str = None, context: str = ""):
    if flags is None:
        flags = get_gobuster_flags(url, context)
    UI.tool_start("GOBUSTER", flags, url)
    cmd = f"gobuster {flags}"
    return run_command(cmd, timeout=300)

def run_nikto(target: str, flags: str = None, context: str = ""):
    if flags is None:
        flags = get_nikto_flags(target, context)
    UI.tool_start("NIKTO", flags, target)
    cmd = f"nikto {flags}"
    return run_command(cmd, timeout=600)

def run_whatweb(target: str, flags: str = None, context: str = ""):
    if flags is None:
        flags = get_whatweb_flags(target, context)
    UI.tool_start("WHATWEB", flags, target)
    cmd = f"whatweb {flags}"
    return run_command(cmd, timeout=120)

# ============================================================
# АНАЛИЗ ВЫВОДА
# ============================================================

def analyze_output(tool: str, output: str):
    analysis = {"found": False, "summary": "", "details": []}
    
    if tool == "nmap":
        open_ports = re.findall(r'(\d+)/tcp\s+open\s+(\w+)', output)
        if open_ports:
            analysis["found"] = True
            analysis["summary"] = f"🔓 {len(open_ports)} open ports discovered"
            for port, service in open_ports[:10]:
                analysis["details"].append(f"Port {port}: {service}")
        else:
            analysis["summary"] = "🔒 No open ports found"
    
    elif tool == "sqlmap":
        if "vulnerable" in output.lower() or "injectable" in output.lower():
            analysis["found"] = True
            analysis["summary"] = "🐛 SQL Injection VULNERABLE!"
            if "boolean" in output.lower():
                analysis["details"].append("Type: Boolean-based Blind")
            if "union" in output.lower():
                analysis["details"].append("Type: Union-based")
            if "time" in output.lower():
                analysis["details"].append("Type: Time-based")
            dbs = re.findall(r'\[\*\*\]\s+(\w+)', output)
            if dbs:
                analysis["details"].append(f"Databases: {', '.join(dbs[:5])}")
        else:
            analysis["summary"] = "🛡️ SQL Injection NOT vulnerable"
    
    elif tool == "gobuster":
        dirs = re.findall(r'/(\S+)\s+\(Status:\s+(\d+)\)', output)
        interesting = [d for d in dirs if d[1] in ["200", "301", "302"]]
        if interesting:
            analysis["found"] = True
            analysis["summary"] = f"📁 {len(interesting)} interesting directories found"
            for path, status in interesting[:10]:
                analysis["details"].append(f"/{path} (HTTP {status})")
        else:
            analysis["summary"] = "📭 No interesting directories found"
    
    elif tool == "nikto":
        vulns = re.findall(r'\+ (.*?):', output)
        real_vulns = [v for v in vulns if any(x in v.lower() for x in ['vulnerable', 'cve', 'xss', 'sql'])]
        if real_vulns:
            analysis["found"] = True
            analysis["summary"] = f"⚠️ {len(real_vulns)} potential vulnerabilities found"
            for v in real_vulns[:5]:
                analysis["details"].append(v[:80])
        else:
            analysis["summary"] = "🛡️ No vulnerabilities detected"
    
    elif tool == "whatweb":
        techs = re.findall(r'\[(.*?)\]', output)
        if techs:
            analysis["found"] = True
            analysis["summary"] = f"🔧 Technologies detected"
            for t in techs[:10]:
                if 'http' not in t.lower() and len(t) < 50:
                    analysis["details"].append(t)
        else:
            analysis["summary"] = "❓ Technologies not detected"
    
    return analysis

# ============================================================
# ИНСТРУМЕНТЫ ДЛЯ API
# ============================================================

TOOLS = [
    {"type": "function", "function": {
        "name": "run_nmap",
        "description": "Nmap port scanner",
        "parameters": {"type": "object", "properties": {"target": {"type": "string"}, "flags": {"type": "string", "default": ""}, "context": {"type": "string", "default": ""}}, "required": ["target"]}
    }},
    {"type": "function", "function": {
        "name": "run_sqlmap",
        "description": "SQL injection scanner",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "flags": {"type": "string", "default": ""}, "context": {"type": "string", "default": ""}}, "required": ["url"]}
    }},
    {"type": "function", "function": {
        "name": "run_gobuster",
        "description": "Directory scanner",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "flags": {"type": "string", "default": ""}, "context": {"type": "string", "default": ""}}, "required": ["url"]}
    }},
    {"type": "function", "function": {
        "name": "run_nikto",
        "description": "Web vulnerability scanner",
        "parameters": {"type": "object", "properties": {"target": {"type": "string"}, "flags": {"type": "string", "default": ""}, "context": {"type": "string", "default": ""}}, "required": ["target"]}
    }},
    {"type": "function", "function": {
        "name": "run_whatweb",
        "description": "Technology detector",
        "parameters": {"type": "object", "properties": {"target": {"type": "string"}, "flags": {"type": "string", "default": ""}, "context": {"type": "string", "default": ""}}, "required": ["target"]}
    }}
]

def execute_tool(tool_name: str, params: dict) -> str:
    if tool_name == "run_nmap":
        result = run_nmap(params["target"], params.get("flags", None), params.get("context", ""))
        analysis = analyze_output("nmap", result["output"])
        return json.dumps({"success": result["success"], "output": result["output"][:3000], "analysis": analysis}, ensure_ascii=False)
    elif tool_name == "run_sqlmap":
        result = run_sqlmap(params["url"], params.get("flags", None), params.get("context", ""))
        analysis = analyze_output("sqlmap", result["output"])
        return json.dumps({"success": result["success"], "output": result["output"][:3000], "analysis": analysis}, ensure_ascii=False)
    elif tool_name == "run_gobuster":
        result = run_gobuster(params["url"], params.get("flags", None), params.get("context", ""))
        analysis = analyze_output("gobuster", result["output"])
        return json.dumps({"success": result["success"], "output": result["output"][:3000], "analysis": analysis}, ensure_ascii=False)
    elif tool_name == "run_nikto":
        result = run_nikto(params["target"], params.get("flags", None), params.get("context", ""))
        analysis = analyze_output("nikto", result["output"])
        return json.dumps({"success": result["success"], "output": result["output"][:3000], "analysis": analysis}, ensure_ascii=False)
    elif tool_name == "run_whatweb":
        result = run_whatweb(params["target"], params.get("flags", None), params.get("context", ""))
        analysis = analyze_output("whatweb", result["output"])
        return json.dumps({"success": result["success"], "output": result["output"][:3000], "analysis": analysis}, ensure_ascii=False)
    return json.dumps({"error": f"Unknown tool: {tool_name}"})

# ============================================================
# КЛАСС АГЕНТА
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
        self.start_time = datetime.now()
    
    def process(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-v4-flash",
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto",
                stream=False,
                temperature=0.3
            )
            
            assistant = response.choices[0].message
            self.messages.append(assistant)
            
            iteration = 0
            while assistant.tool_calls and iteration < 10:
                for tool_call in assistant.tool_calls:
                    tool_name = tool_call.function.name
                    params = json.loads(tool_call.function.arguments)
                    result = execute_tool(tool_name, params)
                    
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                
                response = self.client.chat.completions.create(
                    model="deepseek/deepseek-v4-flash",
                    messages=self.messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    stream=False,
                    temperature=0.3
                )
                
                assistant = response.choices[0].message
                self.messages.append(assistant)
                iteration += 1
            
            return assistant.content or "✅ Operation completed"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def clear(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    def print_stats(self):
        elapsed = datetime.now() - self.start_time
        print(f"\n{Colors.DIM}Session duration: {str(elapsed).split('.')[0]}{Colors.END}")

# ============================================================
# ПРЕМИУМ ПРОМПТ
# ============================================================

def print_prompt():
    print(f"\n{Colors.BOLD}{Colors.GREEN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}│ {Colors.ICON_AGENT} READY{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
    print(f"{Colors.DIM}│ Type your target or use /help for commands{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")

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
    print(f"{Colors.ICON_INFO} Commands: /help | /clear | /exit")
    print(f"{Colors.ICON_FLAG} Smart flag selection based on context")
    print(f"{Colors.DIM}{'='*70}{Colors.END}")

def main():
    print_banner()
    agent = JimAgent()
    
    while True:
        try:
            print_prompt()
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}[{Colors.ICON_USER} jim]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', 'exit', 'quit', '/quit']:
                agent.print_stats()
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}See you next time!{Colors.END}\n")
                break
            
            if user_input.lower() in ['/clear', '/cls', 'clear']:
                agent.clear()
                os.system('clear')
                print_banner()
                continue
            
            if user_input.lower() in ['/help', '/?', 'help']:
                UI.print_box("""
Available Commands:
  /help, /?     - Show this help
  /clear, /cls  - Clear screen  
  /exit, /quit  - Exit Jim

Examples:
  > Scan website example.com for vulnerabilities
  > Test SQL injection on testphp.vulnweb.com/artists.php?id=1
  > Aggressive nmap scan on 192.168.1.1
                """, "JIM HELP MENU", Colors.CYAN)
                continue
            
            if not user_input:
                continue
            
            UI.loading_animation("Analyzing target...", 0.3)
            UI.header("PROCESSING REQUEST", Colors.ICON_ANALYSIS, Colors.PURPLE)
            response = agent.process(user_input)
            
            if response:
                print(f"\n{Colors.BOLD}{Colors.GREEN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}│ {Colors.ICON_AGENT} JIM RESPONSE{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
                
                # Форматируем ответ для красивого вывода
                for line in response.split('\n'):
                    if line.strip():
                        if '✅' in line or 'success' in line.lower():
                            print(f"{Colors.DIM}│{Colors.END} {Colors.GREEN}{line}{Colors.END}")
                        elif '❌' in line or 'error' in line.lower():
                            print(f"{Colors.DIM}│{Colors.END} {Colors.RED}{line}{Colors.END}")
                        elif '⚠️' in line or 'warning' in line.lower():
                            print(f"{Colors.DIM}│{Colors.END} {Colors.YELLOW}{line}{Colors.END}")
                        else:
                            print(f"{Colors.DIM}│{Colors.END} {line}")
                
                print(f"{Colors.BOLD}{Colors.GREEN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} {Colors.YELLOW}Interrupted{Colors.END}")
            continue
        except EOFError:
            print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}Goodbye!{Colors.END}\n")
            break

if __name__ == "__main__":
    main()