#!/usr/bin/env python3
"""
DeepSeek Agent for Kali Linux - Все настройки внутри кода
"""

import openai
import subprocess
import json
import re
import os
import sys
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# ============================================================
# НАСТРОЙКИ (ВСЁ ВНУТРИ КОДА)
# ============================================================

# Модель и параметры API
MODEL_NAME = "deepseek/deepseek-v4-flash"
MAX_ITERATIONS = 15
TEMPERATURE = 0.3
API_TIMEOUT = 60

# Режим отображения (True - отдельные окна, False - вывод в консоль)
USE_SEPARATE_WINDOWS = True

# Параметры таймаутов для утилит (в секундах)
TIMEOUTS = {
    "nmap": 600,
    "sqlmap": 1200,
    "gobuster": 600,
    "nikto": 900,
    "whatweb": 120,
    "hydra": 1800,
    "default": 300
}

# Пути к словарям (Kali Linux)
WORDLISTS = {
    "dirb_common": "/usr/share/wordlists/dirb/common.txt",
    "dirb_big": "/usr/share/wordlists/dirb/big.txt",
    "rockyou": "/usr/share/wordlists/rockyou.txt",
    "seclists": "/usr/share/seclists/Discovery/Web-Content/common.txt"
}

# Системный промпт (можно вынести в файл или оставить здесь)
SYSTEM_PROMPT = """Ты - DeepSeek Agent для Kali Linux. Твоя задача - помогать пользователю в пентесте.

## ВОЗМОЖНОСТИ:
- Запускай nmap, sqlmap, gobuster, nikto, whatweb, hydra
- Анализируй вывод утилит и извлекай важную информацию
- Предлагай следующие шаги на основе результатов

## СТИЛЬ ОТВЕТОВ:
1. Сначала покажи что ты делаешь
2. После выполнения команды проанализируй результаты
3. Дай понятный вывод: что найдено, какие риски

Будь полезным, профессиональным и понятным."""

# ============================================================
# ЗАГРУЗКА API КЛЮЧА ИЗ .env
# ============================================================

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ============================================================
# ЦВЕТА И UI
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
    
    ICON_AGENT = "🤖"
    ICON_USER = "👤"
    ICON_TOOL = "🔧"
    ICON_TERMINAL = "💻"
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"
    ICON_INFO = "ℹ️"
    ICON_WINDOW = "🪟"
    ICON_LOADING = "⏳"

def print_banner():
    os.system('clear' if sys.platform != 'win32' else 'cls')
    print(f"""{Colors.BOLD}{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════════════════╗
║                    🤖 DEEPSEEK AGENT - KALI LINUX 🤖                       ║
║                    🪟 Автономный агент для пентеста 🪟                      ║
╚═══════════════════════════════════════════════════════════════════════════╝{Colors.END}
    """)

def print_check(item: str, status: bool, message: str = ""):
    if status:
        print(f"  {Colors.ICON_SUCCESS} {Colors.GREEN}✓{Colors.END} {item}: {Colors.GREEN}{message or 'OK'}{Colors.END}")
    else:
        print(f"  {Colors.ICON_ERROR} {Colors.RED}✗{Colors.END} {item}: {Colors.RED}{message or 'FAILED'}{Colors.END}")

def print_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}│ {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")

# ============================================================
# ЗАПУСК УТИЛИТ В ОТДЕЛЬНЫХ ОКНАХ
# ============================================================

class TerminalWindow:
    @staticmethod
    def open_window(command: str, title: str = "DeepSeek Agent"):
        print(f"\n{Colors.ICON_WINDOW} {Colors.CYAN}Открываю новое окно: {Colors.BOLD}{title}{Colors.END}")
        print(f"{Colors.DIM}Команда: {command[:100]}{Colors.END}")
        
        script_content = f"""#!/bin/bash
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  {title}"
echo "  Время: $(date)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
{command}
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Процесс завершён. Нажмите Enter для закрытия окна..."
read
"""
        
        script_path = f"/tmp/deepseek_agent_{int(time.time())}.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        
        if sys.platform == "linux":
            terminals = [
                ["gnome-terminal", "--", "bash", script_path],
                ["konsole", "-e", "bash", script_path],
                ["xfce4-terminal", "-e", f"bash {script_path}"],
                ["terminator", "-e", f"bash {script_path}"],
                ["xterm", "-e", f"bash {script_path}"],
            ]
            
            for term_cmd in terminals:
                try:
                    subprocess.run(["which", term_cmd[0]], capture_output=True, check=True)
                    subprocess.Popen(term_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"{Colors.ICON_SUCCESS} {Colors.GREEN}Окно открыто через: {term_cmd[0]}{Colors.END}")
                    return
                except:
                    continue
            
            print(f"{Colors.ICON_WARNING} {Colors.YELLOW}Не удалось найти терминал. Запускаю в фоне...{Colors.END}")
            subprocess.Popen(command, shell=True)

class InteractiveCommand:
    def __init__(self, command: str, timeout: int = 300, separate_window: bool = True, window_title: str = ""):
        self.command = command
        self.timeout = timeout
        self.separate_window = separate_window
        self.window_title = window_title or command[:50]
        
    def execute(self, on_output=None) -> dict:
        if self.separate_window:
            TerminalWindow.open_window(self.command, self.window_title)
            return {
                "success": True,
                "output": f"Команда запущена в отдельном окне: {self.command}",
                "window_opened": True
            }
        
        print(f"\n{Colors.ICON_TERMINAL} {Colors.CYAN}Запуск:{Colors.END} {Colors.BOLD}{self.command}{Colors.END}")
        print(f"{Colors.DIM}{'-' * 70}{Colors.END}")
        
        try:
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                executable='/bin/bash' if sys.platform != 'win32' else None
            )
            
            output_lines = []
            error_lines = []
            
            def read_stdout():
                for line in iter(process.stdout.readline, ''):
                    if line:
                        output_lines.append(line.rstrip())
                        if on_output:
                            on_output(line.rstrip(), 'stdout')
                        else:
                            print(f"{Colors.DIM}{line.rstrip()}{Colors.END}")
                process.stdout.close()
            
            def read_stderr():
                for line in iter(process.stderr.readline, ''):
                    if line:
                        error_lines.append(line.rstrip())
                        if on_output:
                            on_output(line.rstrip(), 'stderr')
                        else:
                            print(f"{Colors.YELLOW}{line.rstrip()}{Colors.END}")
                process.stderr.close()
            
            stdout_thread = threading.Thread(target=read_stdout)
            stderr_thread = threading.Thread(target=read_stderr)
            stdout_thread.start()
            stderr_thread.start()
            
            try:
                process.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait()
                return {"success": False, "output": "\n".join(output_lines), "error": "Timeout", "timed_out": True}
            
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
            
            return {
                "success": process.returncode == 0,
                "output": "\n".join(output_lines),
                "error": "\n".join(error_lines) if error_lines else None,
                "return_code": process.returncode
            }
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

# ============================================================
# УТИЛИТЫ ДЛЯ KALI LINUX
# ============================================================

class KaliTools:
    @staticmethod
    def run_nmap(target: str, flags: str = "-sV") -> dict:
        cmd = f"nmap {flags} {target}"
        return InteractiveCommand(cmd, timeout=TIMEOUTS["nmap"], separate_window=USE_SEPARATE_WINDOWS, window_title=f"Nmap: {target}").execute()
    
    @staticmethod
    def run_sqlmap(url: str, flags: str = "--batch --dbs") -> dict:
        cmd = f"sqlmap -u '{url}' {flags}"
        return InteractiveCommand(cmd, timeout=TIMEOUTS["sqlmap"], separate_window=USE_SEPARATE_WINDOWS, window_title=f"SQLMap: {url[:50]}").execute()
    
    @staticmethod
    def run_gobuster(url: str, wordlist: str = None) -> dict:
        if not wordlist:
            wordlist = WORDLISTS["dirb_common"]
        cmd = f"gobuster dir -u {url} -w {wordlist}"
        return InteractiveCommand(cmd, timeout=TIMEOUTS["gobuster"], separate_window=USE_SEPARATE_WINDOWS, window_title=f"GoBuster: {url}").execute()
    
    @staticmethod
    def run_nikto(target: str) -> dict:
        cmd = f"nikto -h {target}"
        return InteractiveCommand(cmd, timeout=TIMEOUTS["nikto"], separate_window=USE_SEPARATE_WINDOWS, window_title=f"Nikto: {target}").execute()
    
    @staticmethod
    def run_whatweb(target: str) -> dict:
        cmd = f"whatweb {target}"
        return InteractiveCommand(cmd, timeout=TIMEOUTS["whatweb"], separate_window=USE_SEPARATE_WINDOWS, window_title=f"WhatWeb: {target}").execute()
    
    @staticmethod
    def run_custom_command(command: str) -> dict:
        return InteractiveCommand(command, timeout=TIMEOUTS["default"], separate_window=USE_SEPARATE_WINDOWS, window_title="Custom Command").execute()

# ============================================================
# АНАЛИЗ ВЫВОДА
# ============================================================

class OutputAnalyzer:
    @staticmethod
    def analyze_nmap_output(output: str) -> dict:
        analysis = {"open_ports": [], "services": [], "summary": ""}
        port_pattern = r'(\d+)/tcp\s+open\s+(\w+)'
        for match in re.finditer(port_pattern, output):
            analysis["open_ports"].append({"port": match.group(1), "service": match.group(2)})
        analysis["summary"] = f"Найдено {len(analysis['open_ports'])} открытых портов"
        return analysis
    
    @staticmethod
    def analyze_sqlmap_output(output: str) -> dict:
        analysis = {"vulnerable": False, "databases": [], "summary": ""}
        if "vulnerable" in output.lower():
            analysis["vulnerable"] = True
        db_pattern = r'\[\*\*\]\s+(\w+)'
        dbs = re.findall(db_pattern, output)
        if not dbs:
            dbs = re.findall(r'\[\[\s*\]\]\s*(\w+)', output)
        analysis["databases"] = list(set(dbs))[:30]
        analysis["summary"] = f"SQL-инъекция {'найдена' if analysis['vulnerable'] else 'не обнаружена'}. БД: {len(analysis['databases'])}"
        return analysis
    
    @staticmethod
    def analyze_gobuster_output(output: str) -> dict:
        analysis = {"directories": [], "summary": ""}
        dir_pattern = r'/(\S+)\s+\(Status:\s+(\d+)\)'
        for match in re.finditer(dir_pattern, output):
            analysis["directories"].append({"path": match.group(1), "status": match.group(2)})
        analysis["summary"] = f"Найдено {len(analysis['directories'])} директорий"
        return analysis

# ============================================================
# ИНСТРУМЕНТЫ ДЛЯ API
# ============================================================

TOOLS = [
    {"type": "function", "function": {"name": "run_nmap", "description": "Запускает nmap", "parameters": {"type": "object", "properties": {"target": {"type": "string"}, "flags": {"type": "string", "default": "-sV"}}, "required": ["target"]}}},
    {"type": "function", "function": {"name": "run_sqlmap", "description": "Запускает sqlmap", "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "flags": {"type": "string", "default": "--batch --dbs"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "run_gobuster", "description": "Запускает gobuster", "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "wordlist": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "run_nikto", "description": "Запускает nikto", "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}}},
    {"type": "function", "function": {"name": "run_whatweb", "description": "Запускает whatweb", "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}}},
    {"type": "function", "function": {"name": "run_custom_command", "description": "Выполняет команду", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}}
]

def execute_tool(tool_name: str, parameters: dict) -> str:
    try:
        if tool_name == "run_nmap":
            result = KaliTools.run_nmap(parameters["target"], parameters.get("flags", "-sV"))
        elif tool_name == "run_sqlmap":
            result = KaliTools.run_sqlmap(parameters["url"], parameters.get("flags", "--batch --dbs"))
        elif tool_name == "run_gobuster":
            result = KaliTools.run_gobuster(parameters["url"], parameters.get("wordlist"))
        elif tool_name == "run_nikto":
            result = KaliTools.run_nikto(parameters["target"])
        elif tool_name == "run_whatweb":
            result = KaliTools.run_whatweb(parameters["target"])
        elif tool_name == "run_custom_command":
            result = KaliTools.run_custom_command(parameters["command"])
        else:
            return f"Неизвестный инструмент: {tool_name}"
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "success": False})

# ============================================================
# ИНИЦИАЛИЗАЦИЯ И ПРОВЕРКИ
# ============================================================

def initialize_agent() -> tuple:
    """Инициализация агента с проверками"""
    errors = []
    
    print_section(f"{Colors.ICON_LOADING} ПРОВЕРКА ИНИЦИАЛИЗАЦИИ")
    
    # 1. Проверка Python
    print(f"\n{Colors.BOLD}📌 СИСТЕМНЫЕ ТРЕБОВАНИЯ:{Colors.END}")
    py_ok = sys.version_info >= (3, 8)
    print_check("Python версия", py_ok, f"{sys.version_info.major}.{sys.version_info.minor}")
    if not py_ok:
        errors.append("Python 3.8+ required")
    
    # 2. Проверка API ключа
    print(f"\n{Colors.BOLD}🔑 API НАСТРОЙКИ:{Colors.END}")
    if not OPENROUTER_API_KEY:
        errors.append("API ключ не найден в файле .env")
        print_check("OpenRouter API Key", False, "не найден")
    elif not OPENROUTER_API_KEY.startswith("sk-or-v1-"):
        errors.append("Неверный формат API ключа")
        print_check("OpenRouter API Key", False, "неверный формат")
    else:
        print_check("OpenRouter API Key", True, "найден")
    
    # 3. Проверка подключения
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY.startswith("sk-or-v1-"):
        print(f"\n{Colors.BOLD}🌐 ПРОВЕРКА ПОДКЛЮЧЕНИЯ:{Colors.END}")
        print(f"  {Colors.ICON_LOADING} {Colors.BLUE}Тестирование...{Colors.END}")
        
        try:
            client = openai.OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1", timeout=10)
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
                temperature=0.0
            )
            print_check("API Connection", True, "успешно")
        except openai.APIStatusError as e:
            if e.status_code == 402:
                print_check("API Connection", False, "недостаточно средств на балансе")
                errors.append("Пополните баланс на https://openrouter.ai/credits")
            else:
                print_check("API Connection", False, str(e)[:50])
                errors.append(f"API ошибка: {e.status_code}")
        except Exception as e:
            print_check("API Connection", False, str(e)[:50])
            errors.append(f"Ошибка подключения: {str(e)[:50]}")
    
    return len(errors) == 0, errors

# ============================================================
# ОСНОВНОЙ КЛАСС АГЕНТА
# ============================================================

class DeepSeekAgent:
    def __init__(self):
        self.client = None
        self.messages = []
        
    def setup(self):
        if not OPENROUTER_API_KEY:
            return False
        self.client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        return True
    
    def process(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto",
                stream=False,
                temperature=TEMPERATURE
            )
            
            assistant_message = response.choices[0].message
            self.messages.append(assistant_message)
            
            iteration = 0
            while assistant_message.tool_calls and iteration < MAX_ITERATIONS:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    parameters = json.loads(tool_call.function.arguments)
                    print(f"\n{Colors.ICON_TOOL} {Colors.PURPLE}Запуск:{Colors.END} {Colors.BOLD}{tool_name}{Colors.END}")
                    result = execute_tool(tool_name, parameters)
                    
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=self.messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    stream=False,
                    temperature=TEMPERATURE
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

def main():
    print_banner()
    
    # Инициализация
    success, errors = initialize_agent()
    
    if not success:
        print_section(f"{Colors.ICON_ERROR} ОШИБКА ИНИЦИАЛИЗАЦИИ")
        print(f"\n  {Colors.ICON_ERROR} {Colors.RED}Агент не может запуститься:{Colors.END}")
        for error in errors:
            print(f"    • {error}")
        print(f"\n  {Colors.ICON_INFO} Создайте файл .env с содержимым:")
        print(f"  OPENROUTER_API_KEY=sk-or-v1-ваш_ключ")
        print(f"\n  {Colors.ICON_INFO} Получить ключ: https://openrouter.ai/keys")
        sys.exit(1)
    
    # Создаём агента
    agent = DeepSeekAgent()
    if not agent.setup():
        print(f"\n{Colors.ICON_ERROR} {Colors.RED}Не удалось создать клиент API{Colors.END}")
        sys.exit(1)
    
    print_section(f"{Colors.ICON_SUCCESS} ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА")
    print(f"\n  {Colors.ICON_AGENT} {Colors.GREEN}Агент успешно запущен!{Colors.END}")
    print(f"  {Colors.ICON_INFO} Модель: {MODEL_NAME}")
    print(f"  {Colors.ICON_WINDOW} Режим окон: {'ВКЛЮЧЁН' if USE_SEPARATE_WINDOWS else 'ВЫКЛЮЧЕН'}")
    print(f"\n  {Colors.ICON_INFO} Введите /help для справки, /exit для выхода")
    
    # Основной цикл
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}┌─[{Colors.ICON_USER}]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', 'exit', 'quit']:
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
                break
            
            if user_input.lower() == '/clear':
                os.system('clear' if sys.platform != 'win32' else 'cls')
                print_banner()
                agent.clear()
                continue
            
            if user_input.lower() == '/help':
                print(f"""
{Colors.BOLD}📖 КОМАНДЫ:{Colors.END}
  /help     - Эта справка
  /clear    - Очистить экран
  /exit     - Выйти

{Colors.BOLD}💡 ПРИМЕРЫ ЗАПРОСОВ:{Colors.END}
  "Просканируй nmap localhost"
  "Запусти sqlmap на http://testphp.vulnweb.com/artists.php?artist=1"
  "Проверь директории на example.com через gobuster"
                """)
                continue
            
            if not user_input:
                continue
            
            print(f"\n{Colors.ICON_AGENT} {Colors.BLUE}Обработка запроса...{Colors.END}")
            response = agent.process(user_input)
            
            print(f"\n{Colors.BOLD}{Colors.GREEN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
            print(f"{Colors.BOLD}{Colors.GREEN}│ {Colors.ICON_AGENT} ОТВЕТ:{Colors.END}")
            print(f"{Colors.BOLD}{Colors.GREEN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
            for line in response.split('\n'):
                if line.strip():
                    print(f"{Colors.DIM}│{Colors.END} {line}")
            print(f"{Colors.BOLD}{Colors.GREEN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} {Colors.YELLOW}Прервано (Ctrl+C){Colors.END}")
            continue
        except Exception as e:
            print(f"\n{Colors.ICON_ERROR} {Colors.RED}Ошибка: {e}{Colors.END}")

if __name__ == "__main__":
    main()