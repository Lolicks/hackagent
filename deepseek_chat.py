#!/usr/bin/env python3
"""
DeepSeek Agent for Kali Linux - АВТОНОМНЫЙ АГЕНТ
Сам выбирает утилиты, анализирует вывод и принимает решения
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
    
    ICON_AGENT = "🤖"
    ICON_USER = "👤"
    ICON_TOOL = "🔧"
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"
    ICON_INFO = "ℹ️"
    ICON_ANALYSIS = "🔍"
    ICON_DECISION = "🎯"
    ICON_REPORT = "📊"

# ============================================================
# ЗАГРУЗКА КЛЮЧА ИЗ .env
# ============================================================

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print(f"{Colors.ICON_ERROR} {Colors.RED}API ключ не найден в файле .env{Colors.END}")
    print(f"{Colors.ICON_INFO} Создайте файл .env с содержимым: OPENROUTER_API_KEY=sk-or-v1-ваш_ключ")
    sys.exit(1)

# ============================================================
# ЗАГРУЗКА СИСТЕМНОГО ПРОМПТА ИЗ ФАЙЛА
# ============================================================

def load_system_prompt() -> str:
    """Загружает системный промпт из файла system_prompt.txt"""
    
    prompt_paths = [
        "system_prompt.txt",
        "prompts/system_prompt.txt",
        os.path.join(os.path.dirname(__file__), "system_prompt.txt")
    ]
    
    for path in prompt_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"{Colors.ICON_SUCCESS} {Colors.GREEN}Загружен системный промпт из: {path}{Colors.END}")
                    return content
            except Exception as e:
                print(f"{Colors.ICON_WARNING} {Colors.YELLOW}Ошибка чтения {path}: {e}{Colors.END}")
    
    # Промпт по умолчанию
    print(f"{Colors.ICON_WARNING} {Colors.YELLOW}Файл system_prompt.txt не найден! Использую промпт по умолчанию.{Colors.END}")
    return """Ты - автономный ИИ-агент для пентеста Kali Linux. Твоя задача - самостоятельно тестировать цели.

## ТВОЙ АЛГОРИТМ ДЕЙСТВИЙ:
1. ПОЛУЧИ ЦЕЛЬ - пользователь даёт URL, IP или описание ошибки
2. СПЛАНИРУЙ - на основе цели выбери, какие утилиты запустить
3. ВЫПОЛНИ - запусти утилиту и ПОЛУЧИ ЕЁ ВЫВОД
4. ПРОАНАЛИЗИРУЙ - из вывода извлеки важную информацию
5. ПРИМИ РЕШЕНИЕ - на основе анализа реши, что делать дальше
6. ПОВТОРЯЙ - пока не соберёшь достаточно информации
7. СДЕЛАЙ ВЫВОД - выдай итоговый отчёт

## ДОСТУПНЫЕ УТИЛИТЫ:
- run_nmap - сканирование портов (запускай ПЕРВЫМ при тестировании сервера/IP)
- run_sqlmap - поиск SQL-инъекций (если есть URL с параметром)
- run_gobuster - поиск скрытых директорий (после nmap, если есть веб-порт)
- run_nikto - поиск веб-уязвимостей (после nmap, если есть веб-порт)
- run_whatweb - определение технологий (после nmap, если есть веб-порт)

Будь автономным! Сам решай, какие утилиты запускать и когда остановиться."""

SYSTEM_PROMPT = load_system_prompt()

# ============================================================
# ЗАПУСК КОМАНД
# ============================================================

def run_command(command: str, timeout: int = 600, show_output: bool = True) -> dict:
    """Запускает команду и возвращает вывод"""
    if show_output:
        print(f"\n{Colors.ICON_TOOL} {Colors.CYAN}Запуск:{Colors.END} {Colors.BOLD}{command[:150]}{Colors.END}")
        print(f"{Colors.DIM}{'─' * 70}{Colors.END}")
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            executable='/bin/bash' if sys.platform != 'win32' else None
        )
        
        output_lines = []
        for line in iter(process.stdout.readline, ''):
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
        
        process.wait(timeout=timeout)
        return {"success": process.returncode == 0, "output": "\n".join(output_lines)}
    except subprocess.TimeoutExpired:
        process.terminate()
        return {"success": False, "output": "\n".join(output_lines), "error": "Timeout"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

# ============================================================
# АНАЛИЗ ВЫВОДА УТИЛИТ
# ============================================================

def analyze_nmap_output(output: str) -> dict:
    """Анализирует вывод nmap"""
    analysis = {
        "open_ports": [],
        "web_ports": [],
        "interesting_services": [],
        "has_web": False,
        "summary": ""
    }
    
    port_pattern = r'(\d+)/tcp\s+open\s+(\w+)'
    for match in re.finditer(port_pattern, output):
        port = match.group(1)
        service = match.group(2)
        analysis["open_ports"].append({"port": port, "service": service})
        
        if port in ["80", "443", "8080", "8443", "8000"]:
            analysis["web_ports"].append(port)
            analysis["has_web"] = True
            analysis["interesting_services"].append(f"Веб-сервер на порту {port} ({service})")
        elif service in ["mysql", "postgresql", "mongodb"]:
            analysis["interesting_services"].append(f"База данных {service} на порту {port}")
        elif service in ["ssh", "ftp", "telnet"]:
            analysis["interesting_services"].append(f"Доступ по {service.upper()} на порту {port}")
    
    analysis["summary"] = f"Найдено {len(analysis['open_ports'])} открытых портов. Веб-сервер: {'да' if analysis['has_web'] else 'нет'}"
    return analysis

def analyze_sqlmap_output(output: str) -> dict:
    """Анализирует вывод sqlmap"""
    analysis = {
        "vulnerable": False,
        "vulnerability_type": [],
        "databases": [],
        "tables": [],
        "summary": ""
    }
    
    output_lower = output.lower()
    
    if "vulnerable" in output_lower or "injectable" in output_lower:
        analysis["vulnerable"] = True
        if "boolean" in output_lower:
            analysis["vulnerability_type"].append("Boolean-based Blind")
        if "time" in output_lower:
            analysis["vulnerability_type"].append("Time-based Blind")
        if "union" in output_lower:
            analysis["vulnerability_type"].append("Union-based")
    
    db_pattern = r'\[\*\*\]\s+(\w+)'
    analysis["databases"] = list(set(re.findall(db_pattern, output)))[:20]
    
    if analysis["vulnerable"]:
        analysis["summary"] = f"🔴 SQL-инъекция найдена! Тип: {', '.join(analysis['vulnerability_type'])}. БД: {len(analysis['databases'])}"
    else:
        analysis["summary"] = "🟢 SQL-инъекция не обнаружена"
    
    return analysis

def analyze_gobuster_output(output: str) -> dict:
    """Анализирует вывод gobuster"""
    analysis = {
        "found_directories": [],
        "interesting_dirs": [],
        "summary": ""
    }
    
    dir_pattern = r'/(\S+)\s+\(Status:\s+(\d+)\)'
    for match in re.finditer(dir_pattern, output):
        path = match.group(1)
        status = match.group(2)
        analysis["found_directories"].append({"path": path, "status": status})
        if status in ["200", "301", "302"]:
            analysis["interesting_dirs"].append(f"/{path} (Status: {status})")
    
    analysis["summary"] = f"Найдено {len(analysis['found_directories'])} директорий. Интересных: {len(analysis['interesting_dirs'])}"
    return analysis

def analyze_nikto_output(output: str) -> dict:
    """Анализирует вывод nikto"""
    analysis = {
        "vulnerabilities": [],
        "server": None,
        "summary": ""
    }
    
    vuln_pattern = r'\+ (.+?):\s*(.+?)(?:\n|$)'
    for match in re.finditer(vuln_pattern, output):
        title = match.group(1)
        if any(k in title.lower() for k in ['vulnerable', 'cve', 'xss', 'sql', 'rce']):
            analysis["vulnerabilities"].append(title[:80])
    
    server_match = re.search(r'\+ Server:\s*(.+?)(?:\n|$)', output, re.IGNORECASE)
    if server_match:
        analysis["server"] = server_match.group(1).strip()
    
    analysis["summary"] = f"Найдено {len(analysis['vulnerabilities'])} потенциальных уязвимостей"
    return analysis

def analyze_whatweb_output(output: str) -> dict:
    """Анализирует вывод whatweb"""
    analysis = {
        "technologies": [],
        "cms": None,
        "server": None,
        "summary": ""
    }
    
    tech_pattern = r'\[(.*?)\]'
    for tech in re.findall(tech_pattern, output):
        if 'http' not in tech.lower() and len(tech) < 50:
            analysis["technologies"].append(tech)
    
    cms_list = ['wordpress', 'joomla', 'drupal', 'magento']
    for tech in analysis["technologies"]:
        if tech.lower() in cms_list:
            analysis["cms"] = tech
    
    analysis["summary"] = f"Технологии: {', '.join(analysis['technologies'][:5])}"
    return analysis

# ============================================================
# ЗАПУСК УТИЛИТ С ВОЗВРАТОМ АНАЛИЗА
# ============================================================

def run_and_analyze(tool: str, params: dict) -> dict:
    """Запускает утилиту и возвращает анализ"""
    if tool == "nmap":
        target = params.get("target")
        flags = params.get("flags", "-sV -sC")
        result = run_command(f"nmap {flags} {target}", timeout=600)
        if result["output"]:
            analysis = analyze_nmap_output(result["output"])
            return {"success": True, "output": result["output"], "analysis": analysis}
    
    elif tool == "sqlmap":
        url = params.get("url")
        flags = params.get("flags", "--batch --dbs")
        result = run_command(f"sqlmap -u '{url}' {flags}", timeout=1200)
        if result["output"]:
            analysis = analyze_sqlmap_output(result["output"])
            return {"success": True, "output": result["output"], "analysis": analysis}
    
    elif tool == "gobuster":
        url = params.get("url")
        wordlist = params.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
        result = run_command(f"gobuster dir -u {url} -w {wordlist}", timeout=600)
        if result["output"]:
            analysis = analyze_gobuster_output(result["output"])
            return {"success": True, "output": result["output"], "analysis": analysis}
    
    elif tool == "nikto":
        target = params.get("target")
        result = run_command(f"nikto -h {target}", timeout=900)
        if result["output"]:
            analysis = analyze_nikto_output(result["output"])
            return {"success": True, "output": result["output"], "analysis": analysis}
    
    elif tool == "whatweb":
        target = params.get("target")
        result = run_command(f"whatweb {target}", timeout=120)
        if result["output"]:
            analysis = analyze_whatweb_output(result["output"])
            return {"success": True, "output": result["output"], "analysis": analysis}
    
    return {"success": False, "error": "Не удалось выполнить"}

# ============================================================
# ИНСТРУМЕНТЫ ДЛЯ API
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_nmap",
            "description": "Сканирование портов. Запускай ПЕРВЫМ при тестировании сервера/IP",
            "parameters": {"type": "object", "properties": {"target": {"type": "string"}, "flags": {"type": "string", "default": "-sV -sC"}}, "required": ["target"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_sqlmap",
            "description": "Поиск SQL-инъекций. Запускай если есть URL с параметром или подозрение на SQL",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "flags": {"type": "string", "default": "--batch --dbs"}}, "required": ["url"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_gobuster",
            "description": "Поиск скрытых директорий. Запускай после nmap если обнаружен веб-порт",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "wordlist": {"type": "string", "default": "/usr/share/wordlists/dirb/common.txt"}}, "required": ["url"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_nikto",
            "description": "Поиск веб-уязвимостей. Запускай после nmap если есть веб-порт",
            "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_whatweb",
            "description": "Определение технологий. Запускай после nmap если есть веб-порт",
            "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}
        }
    }
]

def execute_tool(tool_name: str, parameters: dict) -> str:
    """Выполняет инструмент и возвращает результат с анализом"""
    
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
        return json.dumps({"error": f"Неизвестный инструмент: {tool_name}"})
    
    if result.get("success"):
        analysis = result.get("analysis", {})
        return json.dumps({
            "success": True,
            "summary": analysis.get("summary", ""),
            "details": analysis
        }, ensure_ascii=False, indent=2)
    else:
        return json.dumps({"success": False, "error": result.get("error", "Ошибка")})

# ============================================================
# ОСНОВНОЙ КЛАСС АГЕНТА
# ============================================================

class DeepSeekAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.test_results = []
    
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
            max_iterations = 20
            while assistant_message.tool_calls and iteration < max_iterations:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    parameters = json.loads(tool_call.function.arguments)
                    
                    print(f"\n{Colors.ICON_TOOL} {Colors.PURPLE}Агент решил запустить:{Colors.END} {Colors.BOLD}{tool_name}{Colors.END}")
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
            
            return assistant_message.content or "Тестирование завершено"
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
║                 🤖 АВТОНОМНЫЙ ИИ-АГЕНТ ДЛЯ ПЕНТЕСТА 🤖                     ║
║              Сам выбирает утилиты, анализирует и принимает решения        ║
╚═══════════════════════════════════════════════════════════════════════════╝{Colors.END}
    """)
    print(f"{Colors.ICON_INFO} {Colors.GREEN}Агент сам решает, что и как тестировать!{Colors.END}")
    print(f"{Colors.ICON_INFO} Просто дайте цель и, если знаете, опишите ошибку")
    print()

def main():
    print_banner()
    agent = DeepSeekAgent()
    
    print(f"{Colors.ICON_AGENT} {Colors.GREEN}Агент готов к автономной работе!{Colors.END}")
    print()
    print(f"{Colors.ICON_INFO} {Colors.YELLOW}Примеры запросов:{Colors.END}")
    print(f"   • Протестируй сервер 192.168.1.100")
    print(f"   • Проверь сайт example.com на уязвимости")
    print(f"   • У меня есть ошибка SQL на test.com/page?id=1 - проверь")
    print(f"   • Найди что можно взломать на target.com")
    print()
    print(f"{Colors.ICON_INFO} Команды: /clear - очистить историю, /exit - выход")
    print(f"{Colors.DIM}{'─' * 70}{Colors.END}")
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.GREEN}┌─[{Colors.ICON_USER} ЦЕЛЬ]{Colors.END} ").strip()
            
            if user_input.lower() in ['/exit', 'exit', 'quit']:
                print(f"\n{Colors.ICON_AGENT} {Colors.GREEN}До свидания!{Colors.END}\n")
                break
            
            if user_input.lower() == '/clear':
                agent.clear()
                os.system('clear' if sys.platform != 'win32' else 'cls')
                print_banner()
                continue
            
            if not user_input:
                continue
            
            print(f"\n{Colors.ICON_AGENT} {Colors.BLUE}Агент анализирует цель и планирует тестирование...{Colors.END}")
            response = agent.process(user_input)
            
            if response:
                print(f"\n{Colors.BOLD}{Colors.CYAN}┌─────────────────────────────────────────────────────────────────────────┐{Colors.END}")
                print(f"{Colors.BOLD}{Colors.CYAN}│ {Colors.ICON_REPORT} ИТОГОВЫЙ ОТЧЁТ{Colors.END}")
                print(f"{Colors.BOLD}{Colors.CYAN}├─────────────────────────────────────────────────────────────────────────┤{Colors.END}")
                for line in response.split('\n'):
                    if line.strip():
                        print(f"{Colors.DIM}│{Colors.END} {line}")
                print(f"{Colors.BOLD}{Colors.CYAN}└─────────────────────────────────────────────────────────────────────────┘{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.ICON_WARNING} {Colors.YELLOW}Прервано (Ctrl+C){Colors.END}")
            continue

if __name__ == "__main__":
    main()