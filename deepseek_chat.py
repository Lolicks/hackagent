#!/usr/bin/env python3
"""
Jim - AI-Powered Pentesting Assistant for Kali Linux
Автономный ИИ-агент для тестирования на проникновение
"""

import openai
import subprocess
import json
import re
import os
import sys
import time
import threading
import signal
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# ============================================================
# ВЕРСИЯ
# ============================================================

VERSION = "2.0.0"

# ============================================================
# ОБРАБОТКА АРГУМЕНТОВ КОМАНДНОЙ СТРОКИ
# ============================================================

if len(sys.argv) > 1:
    if sys.argv[1] in ["-v", "--version"]:
        print(f"Jim AI Agent v{VERSION}")
        sys.exit(0)
    elif sys.argv[1] in ["-u", "--update", "-update"]:
        print("🔄 Обновление Jim AI Agent...")
        # Путь к текущему скрипту
        current_file = os.path.abspath(__file__)
        jim_dir = os.path.dirname(current_file)
        parent_dir = os.path.dirname(jim_dir)
        
        # Переход в директорию и git pull или копирование новой версии
        try:
            os.chdir(jim_dir)
            result = subprocess.run(["git", "pull"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Jim успешно обновлён!")
                print(f"📁 Обновление из: {jim_dir}")
            else:
                print("⚠️ Git не найден, скачиваю новую версию...")
                subprocess.run(["wget", "-O", "jim.py", "https://raw.githubusercontent.com/yourrepo/jim/main/jim.py"], check=False)
                subprocess.run(["chmod", "+x", "jim.py"])
        except Exception as e:
            print(f"❌ Ошибка обновления: {e}")
        sys.exit(0)
    elif sys.argv[1] in ["-h", "--help", "help"]:
        print("""
Jim AI Agent - Автономный помощник для пентеста

Использование:
    jim                    Запустить агента в интерактивном режиме
    jim -h, --help         Показать эту справку
    jim -v, --version      Показать версию
    jim -u, --update       Обновить Jim до последней версии

Команды внутри агента:
    /help                  Показать справку
    /clear                 Очистить экран
    /exit                  Выйти

Примеры:
    jim
    > Протестируй сайт example.com
    > Найди SQL-инъекции на testphp.vulnweb.com/artists.php?artist=1
""")
        sys.exit(0)

# ============================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# ============================================================

current_process = None
interrupted = False

def signal_handler(sig, frame):
    global current_process, interrupted
    print(f"\n\n⚠️  Получен сигнал прерывания! Останавливаю процесс...")
    interrupted = True
    if current_process:
        try:
            current_process.terminate()
            print("✅ Процесс остановлен")
        except:
            pass

signal.signal(signal.SIGINT, signal_handler)

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
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'
    
    ICON_AGENT = "🐍"
    ICON_USER = "👤"
    ICON_TOOL = "🔧"
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"
    ICON_INFO = "ℹ️"
    ICON_ANALYSIS = "🔍"
    ICON_DECISION = "🎯"
    ICON_REPORT = "📊"
    ICON_STOP = "🛑"

# ============================================================
# ЗАГРУЗКА НАСТРОЕК
# ============================================================

def get_jim_dir():
    """Возвращает директорию установки Jim"""
    # Пробуем найти jim.py
    possible_paths = [
        os.path.expanduser("~/jim-ai"),
        os.path.dirname(os.path.abspath(__file__)),
        os.path.expanduser("~/.jim"),
        "/opt/jim-ai"
    ]
    
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "jim.py")):
            return path
    
    # Если не нашли, используем директорию скрипта
    return os.path.dirname(os.path.abspath(__file__))

JIM_DIR = get_jim_dir()
ENV_PATH = os.path.join(JIM_DIR, ".env")
PROMPT_PATH = os.path.join(JIM_DIR, "system_prompt.txt")

# Загрузка API ключа
load_dotenv(ENV_PATH)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ============================================================
# ЗАГРУЗКА ПРОМПТА
# ============================================================

def load_system_prompt() -> str:
    """Загружает системный промпт"""
    prompt_paths = [
        PROMPT_PATH,
        os.path.join(JIM_DIR, "system_prompt.txt"),
        "system_prompt.txt"
    ]
    
    for path in prompt_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass
    
    # Промпт по умолчанию
    return """Ты - Jim, автономный ИИ-агент для пентеста Kali Linux. Твоё имя Jim.

## ТВОЙ АЛГОРИТМ ДЕЙСТВИЙ:
1. Получи цель от пользователя
2. Выбери подходящие утилиты (nmap, sqlmap, gobuster, nikto, whatweb)
3. Проанализируй вывод каждой утилиты
4. Прими решение о следующих действиях на основе анализа
5. Выдай итоговый отчёт с найденными уязвимостями

## ДОСТУПНЫЕ УТИЛИТЫ:
- run_nmap - сканирование портов
- run_sqlmap - поиск SQL-инъекций
- run_gobuster - поиск директорий
- run_nikto - поиск веб-уязвимостей
- run_whatweb - определение технологий

Будь автономным, профессиональным и дружелюбным!"""

SYSTEM_PROMPT = load_system_prompt()

# ============================================================
# ЗАПУСК КОМАНД
# ============================================================

def run_command(command: str, timeout: int = 600, show_output: bool = True) -> dict:
    """Запускает команду с возможностью прерывания"""
    global current_process, interrupted
    
    if show_output:
        print(f"\n{Colors.ICON_TOOL} {Colors.CYAN}Jim запускает:{Colors.END} {Colors.BOLD}{command[:150]}{Colors.END}")
        print(f"{Colors.DIM}{'─' * 70}{Colors.END}")
        print(f"{Colors.ICON_INFO} {Colors.DIM}Нажмите Ctrl+C для остановки{Colors.END}")
    
    interrupted = False
    output_lines = []
    
    try:
        current_process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            executable='/bin/bash' if sys.platform != 'win32' else None
        )
        
        for line in iter(current_process.stdout.readline, ''):
            if interrupted:
                current_process.terminate()
                print(f"\n{Colors.ICON_STOP} {Colors.YELLOW}Сканирование остановлено{Colors.END}")
                return {"success": False, "output": "\n".join(output_lines), "interrupted": True}
            
            if line:
                output_lines.append(line.rstrip())
                if show_output:
                    if 'vulnerable' in line.lower() or 'injectable' in line.lower():
                        print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                    elif 'open' in line.lower() and 'tcp' in line.lower():
                        print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                    elif 'error' in line.lower() or 'failed' in line.lower():
                        print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                    elif 'database' in line.lower() or 'table' in line.lower():
                        print(f"{Colors.CYAN}{line.rstrip()}{Colors.END}")
                    else:
                        print(line.rstrip())
        
        current_process.wait(timeout=timeout)
        return {"success": current_process.returncode == 0, "output": "\n".join(output_lines)}
        
    except subprocess.TimeoutExpired:
        if current_process:
            current_process.terminate()
        return {"success": False, "output": "\n".join(output_lines), "error": "Timeout"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}
    finally:
        current_process = None

# ============================================================
# АНАЛИЗ ВЫВОДА
# ============================================================

def analyze_nmap_output(output: str) -> dict:
    analysis = {"open_ports": [], "web_ports": [], "has_web": False, "summary": ""}
    port_pattern = r'(\d+)/tcp\s+open\s+(\w+)'
    for match in re.finditer(port_pattern, output):
        port = match.group(1)
        service = match.group(2)
        analysis["open_ports"].append({"port": port, "service": service})
        if port in ["80", "443", "8080", "8443", "8000"]:
            analysis["web_ports"].append(port)
            analysis["has_web"] = True
    analysis["summary"] = f"Найдено {len(analysis['open_ports'])} открытых портов"
    return analysis

def analyze_sqlmap_output(output: str) -> dict:
    analysis = {"vulnerable": False, "vulnerability_type": [], "databases": [], "summary": ""}
    output_lower = output.lower()
    if "vulnerable" in output_lower or "injectable" in output_lower:
        analysis["vulnerable"] = True
        if "boolean" in output_lower:
            analysis["vulnerability_type"].append("Boolean-based Blind")
        if "union" in output_lower:
            analysis["vulnerability_type"].append("Union-based")
    db_pattern = r'\[\*\*\]\s+(\w+)'
    analysis["databases"] = list(set(re.findall(db_pattern, output)))[:20]
    if analysis["vulnerable"]:
        analysis["summary"] = f"🔴 SQL-инъекция найдена! БД: {len(analysis['databases'])}"
    else:
        analysis["summary"] = "🟢 SQL-инъекция не обнаружена"
    return analysis

def analyze_gobuster_output(output: str) -> dict:
    analysis = {"found_directories": [], "summary": ""}
    dir_pattern = r'/(\S+)\s+\(Status:\s+(\d+)\)'
    for match in re.finditer(dir_pattern, output):
        analysis["found_directories"].append({"path": match.group(1), "status": match.group(2)})
    analysis["summary"] = f"Найдено {len(analysis['found_directories'])} директорий"
    return analysis

def analyze_nikto_output(output: str) -> dict:
    analysis = {"vulnerabilities": [], "summary": ""}
    vuln_pattern = r'\+ (.+?):'
    for match in re.finditer(vuln_pattern, output):
        title = match.group(1)
        if any(k in title.lower() for k in ['vulnerable', 'cve', 'xss', 'sql']):
            analysis["vulnerabilities"].append(title[:80])
    analysis["summary"] = f"Найдено {len(analysis['vulnerabilities'])} уязвимостей"
    return analysis

def analyze_whatweb_output(output: str) -> dict:
    analysis = {"technologies": [], "summary": ""}
    tech_pattern = r'\[(.*?)\]'
    for tech in re.findall(tech_pattern, output):
        if 'http' not in tech.lower() and len(tech) < 50:
            analysis["technologies"].append(tech)
    analysis["summary"] = f"Технологии: {', '.join(analysis['technologies'][:5])}"
    return analysis

# ============================================================
# ЗАПУСК УТИЛИТ
# ============================================================

def run_and_analyze(tool: str, params: dict) -> dict:
    if tool == "nmap":
        result = run_command(f"nmap -sV -sC {params.get('target')}", timeout=600)
        if result.get("interrupted"):
            return {"success": False, "interrupted": True}
        if result["output"]:
            return {"success": True, "analysis": analyze_nmap_output(result["output"])}
    
    elif tool == "sqlmap":
        result = run_command(f"sqlmap -u '{params.get('url')}' --batch --dbs", timeout=1200)
        if result.get("interrupted"):
            return {"success": False, "interrupted": True}
        if result["output"]:
            return {"success": True, "analysis": analyze_sqlmap_output(result["output"])}
    
    elif tool == "gobuster":
        result = run_command(f"gobuster dir -u {params.get('url')} -w /usr/share/wordlists/dirb/common.txt", timeout=600)
        if result.get("interrupted"):
            return {"success": False, "interrupted": True}
        if result["output"]:
            return {"success": True, "analysis": analyze_gobuster_output(result["output"])}
    
    elif tool == "nikto":
        result = run_command(f"nikto -h {params.get('target')}", timeout=900)
        if result.get("interrupted"):
            return {"success": False, "interrupted": True}
        if result["output"]:
            return {"success": True, "analysis": analyze_nikto_output(result["output"])}
    
    elif tool == "whatweb":
        result = run_command(f"whatweb {params.get('target')}", timeout=120)
        if result.get("interrupted"):
            return {"success": False, "interrupted": True}
        if result["output"]:
            return {"success": True, "analysis": analyze_whatweb_output(result["output"])}
    
    return {"success": False, "error": "Не удалось выполнить"}

# ============================================================
# ИНСТРУМЕНТЫ ДЛЯ API
# ============================================================

TOOLS = [
    {"type": "function", "function": {"name": "run_nmap", "description": "Сканирование портов", "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}}},
    {"type": "function", "function": {"name": "run_sqlmap", "description": "Поиск SQL-инъекций", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "run_gobuster", "description": "Поиск директорий", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "run_nikto", "description": "Поиск веб-уязвимостей", "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}}},
    {"type": "function", "function": {"name": "run_whatweb", "description": "Определение технологий", "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}}}
]

def execute_tool(tool_name: str, parameters: dict) -> str:
    if tool_name == "run_nmap":
        result = run_and_analyze("nmap", parameters)
    elif tool_name == "run_sqlmap":
        result = run_and_analyze("sqlmap", parameters)
    elif tool_name == "run_gobuster":
        result = run_and_analyze("gobuster", parameters)
    elif tool_name == "run_nikto":
        result = run_and_analyze("nikto", parameters)
    elif tool_name == "run_whatweb":
        result = run_and_analyze("whatweb", parameters)
    else:
        return json.dumps({"error": f"Неизвестный инструмент"})
    
    if result.get("interrupted"):
        return json.dumps({"success": False, "interrupted": True, "summary": "Остановлено пользователем"})
    
    if result.get("success"):
        analysis = result.get("analysis", {})
        return json.dumps({"success": True, "summary": analysis.get("summary", "")}, ensure_ascii=False)
    
    return json.dumps({"success": False, "error": result.get("error", "Ошибка")})

# ============================================================
# ОСНОВНОЙ КЛАСС JIM
# ============================================================

class JimAgent:
    def __init__(self):
        if not OPENROUTER_API_KEY:
            print(f"{Colors.ICON_ERROR} {Colors.RED}API ключ не найден!{Colors.END}")
            print(f"{Colors.ICON_INFO} Создайте {ENV_PATH} с содержимым: OPENROUTER_API_KEY=sk-or-v1-ключ")
            sys.exit(1)
        
        self.client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
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
            
            assistant_message = response.choices[0].message
            self.messages.append(assistant_message)
            
            iteration = 0
            while assistant_message.tool_calls and iteration < 20:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    parameters = json.loads(tool_call.function.arguments)
                    
                    print(f"\n{Colors.ICON_TOOL} {Colors.PURPLE}Jim решил запустить:{Colors.END} {Colors.BOLD}{tool_name}{Colors.END}")
                    result = execute_tool(tool_name, parameters)
                    
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
                
                assistant_message = response.choices[0].message
                self.messages.append(assistant_message)
                iteration += 1
            
            return assistant_message.content or "Готово!"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def clear(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# ============================================================
# ЗАПУСК
# ============================================================

def print_banner():
    os.system('clear' if sys.platform != 'win32' else 'cls')
    print(f"""{Colors.BOLD}{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║    ██╗ ██╗███╗   ███╗    █████╗ ██╗     ███████╗███╗   ██╗████████╗       ║
║    ██║ ██║████╗ ████║   ██╔══██╗██║     ██╔════╝████╗  ██║╚══██╔══╝       ║
║    ██║ ██║██╔████╔██║   ███████║██║     █████╗  ██╔██╗ ██║   ██║          ║
║    ██║ ██║██║╚██╔╝██║   ██╔══██║██║     ██╔══╝  ██║╚██╗██║   ██║          ║
║    ███████║██║ ╚═╝ ██║██╗██║  ██║███████╗███████╗██║ ╚████║   ██║          ║
║    ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝          ║
║                                                                           ║
║                    🤖 JIM AI - ПЕНТЕСТ АССИСТЕНТ 🤖                        ║
║                         v{VERSION} - Автономный режим                       ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝{Colors.END}
    """)
    print(f"{Colors.ICON_INFO} {Colors.GREEN}Jim готов к работе!{Colors.END}")
    print(f"{Colors.ICON_INFO} Нажмите Ctrl+C для остановки сканирования")
    print(f"{Colors.ICON_INFO} Команды: /help, /clear, /exit")
    print()

def main():
    print_banner()
    jim = JimAgent()
    
    print(f"{Colors.ICON_AGENT} {Colors.GREEN}Jim слушает...{Colors.END}")
    print(f"{Colors.DIM}{'─' * 70}{Colors.END}")
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}┌─[{Colors.ICON_USER} JIM]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', 'exit', 'quit']:
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
                break
            
            if user_input.lower() in ['/help', 'help']:
                print("""
Jim AI Agent - Доступные команды:
    /help      - Показать справку
    /clear     - Очистить экран
    /exit      - Выйти

Примеры запросов:
    > Протестируй сайт example.com
    > Найди SQL-инъекции на testphp.vulnweb.com/artists.php?artist=1
    > Просканируй порты на scanme.nmap.org
""")
                continue
            
            if user_input.lower() == '/clear':
                jim.clear()
                os.system('clear' if sys.platform != 'win32' else 'cls')
                print_banner()
                continue
            
            if not user_input:
                continue
            
            print(f"\n{Colors.ICON_AGENT} {Colors.BLUE}Jim анализирует цель...{Colors.END}")
            response = jim.process(user_input)
            
            if response:
                print(f"\n{Colors.BOLD}{Colors.GREEN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}│ {Colors.ICON_AGENT} JIM:{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
                for line in response.split('\n'):
                    if line.strip():
                        print(f"{Colors.DIM}│{Colors.END} {line}")
                print(f"{Colors.BOLD}{Colors.GREEN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} {Colors.YELLOW}Для выхода введите /exit{Colors.END}")
            continue

if __name__ == "__main__":
    main()